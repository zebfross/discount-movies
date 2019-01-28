from bs4 import BeautifulSoup as bs
from urllib.request import (
    urlopen, urlparse, urlunparse, urlretrieve, Request)
from . import utils
import os
import sys
import json
import re

baseUrl = 'http://microsoft.com'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

headers={
    'User-Agent':user_agent
    ,"authority": "www.microsoft.com" 
    ,"cache-control": "max-age=0" 
    ,"upgrade-insecure-requests": "1" 
    ,"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" 
    ,"accept-language": "en-US,en;q=0.9" 
}

startReg = "^ReactDOM\.hydrate\(React\.createElement\(OneRF_DynamicModules\.(ButtonPanel|ProductPrice)\, "
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

    def __init__(self, id, href, title):
        self.prices = []
        self.id = id
        self.href = href
        self.title = title
    
    def addPrice(self, price):
        if price not in self.prices:
            self.prices.append(price)

    def __str__(self):
        formatted = self.id + " "
        for price in self.prices:
            formatted = formatted + str(price) + " -- "
        
        return formatted

    def toJsonObject(self):
        obj = {}
        for key in self.__dict__:
            if key is not 'prices':
                obj[key] = self.__dict__[key]

        obj['prices'] = []
        for price in self.prices:
            obj['prices'].append(price.toJsonObject())
        
        return obj

def parseJson(jsonString):
    if jsonString[0] is not '{':
        raise Exception('unexpected start of json ' + jsonString)
        
    stripped = utils.cleanString(jsonString)
    utils.log().debug(stripped)
    return json.loads(stripped, strict=False)
        
def parseJavascriptLine(line, product):
    #invalid_string = '{"Value":trume,"ConditionMap":null}'
    #decoded = bytes(invalid_string, 'utf-8').decode('utf-8', 'ignore')
    #print(decoded)
    #decoded = utils.cleanString(decoded)
    #print(decoded)
    #print(bytes(invalid_string, 'utf-8').decode('ascii', ))
    #print(bytes(invalid_string, 'utf-8').decode("utf-8", 'ignore'))
    #print(bytes(decoded, 'utf8')
    #res = json.loads(bytes(invalid_string, 'utf-8').decode("utf-8", 'ignore'))
    #return
    #utils.log().debug(res)

    if not re.search(reactReg, line):
        return

    stripped = re.sub(reactReg, "\g<json>", line)

    strippedJson = parseJson(stripped)

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
    elif 'SkuDisplayData' in strippedJson:
        for skuNum in strippedJson['SkuDisplayData']:
            sku = strippedJson['SkuDisplayData'][skuNum]
            price = Price('Buy', sku['CurrentFormattedPrice'], sku['OriginalFormattedPrice'])
            product.addPrice(price)
            utils.log().debug(price)
    else:
        raise Exception("no Actions or SkuDisplayData in " + strippedJson)

def requestSoup(url):
    try:
        request=Request(url,None,headers) #The assembled request
        response = urlopen(request)
        return bs(response.read().decode('utf-8', 'ignore'), "html.parser")
    except Exception as e:
        utils.log().exception("error getting url: " + url)
        return ""

def parseMoviePage(href, id, title):
    url = baseUrl + href
    
    soup = requestSoup(url)

    product = Product(id, href, title)
    scripts = soup.findAll('script')
    if len(scripts) == 0:
        utils.log().error('no scripts found on page to extract product info')
        return None
        
    for script in scripts:
        lines = script.text.split('\n')
        for line in lines:
            parseJavascriptLine(line, product)

    utils.log().info("Product completed " + str(product))

    return product


def parseMoviesPage(pageUrl, insertMovie):
    url = baseUrl + pageUrl
    try:
        soup = requestSoup(url)

        #parseMoviePage(baseUrl, '/en-us/p/the-first-purge/8d6kgwxn2nk6', '8d6kgwxn2nk6')
        #parseMoviePage(baseUrl, '/en-us/p/the-nightmare-before-christmas/8d6kgwzl6186', '8d6kgwzl6186')
        divs = soup.findAll("div", class_="m-channel-placement-item")
        if len(divs) == 0:
            divs = soup.findAll("section", class_="m-product-placement-item")

            if len(divs) == 0:
                raise Exception("no sections with class m-product-placement-item or divs with class m-channel-placement-item")

        for productDiv in divs:
            anchor = productDiv.findNext('a')
            if not anchor.has_attr('href'):
                utils.log().error(anchor)
                continue

            _id = ''
            title = ''
            if not anchor.has_attr('data-m'):
                utils.log().warning(anchor)
            else:
                strippedJson = parseJson(anchor['data-m'])
                if 'pid' in strippedJson:
                    _id = strippedJson['pid']
                else:
                    utils.log().warning('no product id found: ' + anchor['data-m'])
                
                if 'cN' in strippedJson:
                    title = strippedJson['cN']
                
            href = anchor['href']

            utils.log().info("found product: " + href)
            product = parseMoviePage(href, _id, title)
            if product is not None:
                insertMovie(product.toJsonObject())
            else:
                utils.log().warning('no product on page: %s', href)
    except Exception as e:
        utils.log().exception(e)
        
def parseMovies(insertMovie):
    soup = requestSoup('https://www.microsoft.com/en-us/store/movies-and-tv')

    # parse main sales
    saleLinks = soup.select('.m-feature-channel a')
    
    if len(saleLinks) == 0:
        utils.log().exception('no .m-feature-channel sale links found')
    else:
        for link in saleLinks:
            parseMoviesPage(link['href'], insertMovie)

    # parse flash sales - url is random, so we need to find it on the homepage
    
    heroLinks = soup.select('.pad-multi-hero a[href*="spider"]')

    if len(heroLinks) > 0:
        for link in heroLinks:
            parseMoviesPage(link['href'], insertMovie)
    else:
        utils.log().info('did not find flash sale')
