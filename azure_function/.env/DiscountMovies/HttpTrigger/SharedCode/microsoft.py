from bs4 import BeautifulSoup as bs
from urllib.request import (
    urlopen, urlparse, urlunparse, urlretrieve, Request)
from . import utils
import os
import sys
import json
import re

baseUrl = 'http://microsoft.com'
moviesPage = '/en-us/store/movies-and-tv'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

headers={
    'User-Agent':user_agent
    ,"authority": "www.microsoft.com" 
    ,"cache-control": "max-age=0" 
    ,"upgrade-insecure-requests": "1" 
    ,"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" 
    ,"accept-language": "en-US,en;q=0.9" 
}

startReg = "^ReactDOM\.hydrate\(React\.createElement\(OneRF_DynamicModules\.(ButtonPanel|ProductPrice|DescriptionBlock)\, "
endReg = '\)\, document\.getElementById\("react_[a-zA-Z0-9]+"\)\);'
jsonReg = "(?P<json>.*)"
reactReg = startReg + jsonReg + endReg

class Price:

    def __init__(self, priceType, amount, originalAmount):
        self.priceType = priceType
        self.amount = utils.currencyToFloat(amount)
        self.originalAmount = utils.currencyToFloat(originalAmount)
        self.isOnSale = self.amount < self.originalAmount

    def __eq__(self, other):
        if self.priceType == other.priceType and \
        self.amount == other.amount:
            return True
        else:
            return False
    
    def __str__(self):
        return self.priceType + " " + str(self.amount) + " " + str(self.isOnSale)

    def toJsonObject(self):
        return self.__dict__

class Product:

    def __init__(self, href, id, title, prices):
        self.href = href
        self.id = id
        self.title = title
        self.prices = prices
    
    def addPrice(self, price):
        if price not in self.prices:
            self.prices.append(price)

    def __str__(self):
        formatted = self.id + " "
        for price in self.prices:
            formatted = formatted + str(price) + " -- "
        
        return formatted

    def isValid(self):
        if not self.id or not self.title or not len(self.prices) or not self.href:
            return False
        else:
            return True

    def toJsonObject(self):
        obj = {}
        for key in self.__dict__:
            if key is not 'prices':
                obj[key] = self.__dict__[key]

        obj['prices'] = []
        for price in self.prices:
            obj['prices'].append(price.toJsonObject())
        
        return obj
    
class MicrosoftScraper:

    def __init__(self):
        self.linksScraped = set()

    @staticmethod
    def parseJson(jsonString):
        if jsonString[0] is not '{':
            raise Exception('unexpected start of json ' + jsonString)
            
        stripped = utils.cleanString(jsonString)
        utils.log().debug(stripped)
        return json.loads(stripped, strict=False)
            
    @staticmethod
    def parseJavascriptLine(line, product):
        if not re.search(reactReg, line):
            utils.log().debug('no match on regex')
            return

        stripped = re.sub(reactReg, "\g<json>", line)

        strippedJson = MicrosoftScraper.parseJson(stripped)

        if 'Actions' in strippedJson:
            for action in strippedJson['Actions']:
                utils.log().debug(action)
                if 'Label' in action:
                    label = action['Label']
                    if not label['IncludePrice']:
                        utils.log().debug('label doesn\'t include price--skipping')
                        continue

                    price = Price(label['LabelPrefix'], label['CurrentPrice'], label['OriginalPrice'])
                    product.addPrice(price)
                    utils.log().debug(price)
                else:
                    raise Exception('no Label in action ' + action)
        elif 'SkuDisplayData' in strippedJson and strippedJson['SkuDisplayData'] != None:
            for skuNum in strippedJson['SkuDisplayData']:
                sku = strippedJson['SkuDisplayData'][skuNum]
                price = Price('Buy', sku['CurrentFormattedPrice'], sku['OriginalFormattedPrice'])
                product.addPrice(price)
                utils.log().debug(price)

        if 'ProductDisplayData' in strippedJson and 'ProductId' in strippedJson:
            if not product.title:
                product.title = strippedJson['ProductDisplayData']['Title']['VisibleContent']
            if not product.id:
                product.id = strippedJson['ProductId']

    @staticmethod
    def requestSoupWithRetry(url):
        utils.log().info('requesting url: %s', url)
        retriesLeft = 3
        while retriesLeft > 0:
            try:
                request=Request(url,None,headers) #The assembled request
                response = urlopen(request)
                return bs(response.read().decode('utf-8', 'ignore'), "html.parser")
            except Exception as e:
                utils.log().exception("error getting url (Retries left: " + str(retriesLeft) + "): " + url)
                retriesLeft -= 1

        utils.log().exception("error getting url (no retries left): " + url)
        return None

    def parseMoviePage(self, href, insertMovie):
        if href in self.linksScraped:
            return None

        self.linksScraped.add(href)
        url = baseUrl + href
        
        soup = MicrosoftScraper.requestSoupWithRetry(url)
        if not soup:
            return None

        product = Product(href, '', '', [])
        scripts = soup.findAll('script')
        if len(scripts) == 0:
            utils.log().error('no scripts found on page to extract product info')
            return None
            
        for script in scripts:
            lines = script.text.split('\n')
            for line in lines:
                MicrosoftScraper.parseJavascriptLine(line, product)

        utils.log().info("Product completed " + str(product))
            
        if product.isValid():
            insertMovie(product.toJsonObject())

        return product

    def parseMoviesPage(self, pageUrl, insertMovie):
        if pageUrl in self.linksScraped:
            return None

        self.linksScraped.add(pageUrl)
        url = baseUrl + pageUrl
        try:
            # this isn't a movie collection page, so treat it as a single movie page
            if 'collection' not in url:
                utils.log().info('url %s not a collection', pageUrl)
                return self.parseMoviePage(pageUrl, insertMovie)
                
            soup = MicrosoftScraper.requestSoupWithRetry(url)

            links = soup.select("div.m-channel-placement-item a")
            if len(links) == 0:
                links = soup.select("section.m-product-placement-item a")

                if len(links) == 0:
                    links = soup.select("div.m-content-placement a")

                    if len(links) == 0:
                        raise Exception("missing section.m-product-placement-item or div.m-channel-placement-item or div.m-content-placement")

            for productLink in links:
                href = productLink['href']
                utils.log().debug("found product: " + href)
                if 'collection' in href:
                    self.parseMoviesPage(href, insertMovie)
                else:
                    self.parseMoviePage(href, insertMovie)
        except Exception as e:
            utils.log().exception(e)
            
    def parseMovies(self, insertMovie):
        soup = MicrosoftScraper.requestSoupWithRetry(baseUrl + moviesPage)
        self.linksScraped = set()

        # parse main sales
        saleLinks = soup.select('.m-feature-channel a')
        
        if len(saleLinks) == 0:
            utils.log().exception('no .m-feature-channel sale links found')
        else:
            for link in saleLinks:
                self.parseMoviesPage(link['href'], insertMovie)

        # parse flash sales - url is random, so we need to find it on the homepage
        
        heroLinks = soup.select('.pad-multi-hero a[href*="sale"]')

        if len(heroLinks) > 0:
            for link in heroLinks:
                self.parseMoviesPage(link['href'], insertMovie)
        else:
            utils.log().info('did not find flash sale')
