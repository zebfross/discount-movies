import unittest
from HttpTrigger.SharedCode import microsoft, utils
from unittest import mock
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

lineStart = 'ReactDOM.hydrate(React.createElement(OneRF_DynamicModules.ButtonPanel, '
lineEnd = '), document.getElementById("react_abc"));'
testJson = '{"Actions":[{"Label":{"IncludePrice":true,"LabelPrefix":"Rent ","OriginalPrice":"$7.99","CurrentPrice":"$0.99"}}],"ProductDisplayData":{"Title":{"VisibleContent":"Test Title"}},"ProductId":"123"}'
homePageHtml = """<html>
    <div class="m-feature-channel"><a href="/collection/movies"></a></div>
    <div class="m-feature-channel"><a href="/test/movie"></a></div>
</html>
"""
moviePageHtml = """<html>
    <script>{0}{1}{2}</script>
</html>
""".format(lineStart, testJson, lineEnd)
moviesPageHtml = """<html>
<div class="m-channel-placement-item"><a href="/test/movie"></a></div>
<div class="m-channel-placement-item"><a href="/test/movie2"></a></div>
</html>
"""
    
def mock_requestSoupWithRetry(url):
    if "collection" in url:
        return bs(moviesPageHtml, 'html.parser')
    elif "movies-and-tv" in url:
        return bs(homePageHtml, "html.parser")
    else:
        return bs(moviePageHtml, "html.parser")

def mock_parseAndInsert(url, insertMovie):
    return insertMovie(None)

class TestMicrosoft(unittest.TestCase):

    def test_parseJson(self):
        obj = microsoft.MicrosoftScraper.parseJson('{"a":3}')
        self.assertEqual(3, obj['a'], 'parseJson should parse json string')

        obj = microsoft.MicrosoftScraper.parseJson('{"Value":trume}')
        self.assertTrue(obj['Value'], 'parseJson should parse strings with invalid characters')

    def test_productIsValid(self):
        price = microsoft.Price('Buy', '3', '3')
        prod = microsoft.Product('http://test.com', '3', 'title', [price])
        self.assertTrue(prod.isValid(), "product with all properties should be valid")

        prod = microsoft.Product('', 'id', 'title', [price])
        self.assertFalse(prod.isValid(), "product without href is invalid")

        prod = microsoft.Product('href', '', 'title', [price])
        self.assertFalse(prod.isValid(), "product without id is invalid")
        
        prod = microsoft.Product('href', 'id', '', [price])
        self.assertFalse(prod.isValid(), "product without title is invalid")
        
        prod = microsoft.Product('href', 'id', 'title', [])
        self.assertFalse(prod.isValid(), "product without price is invalid")

    def test_parseJavascriptLine(self):
        prod = microsoft.Product('', '', '', [])
        json = '{"Actions":[{"Label":{"IncludePrice":true,"LabelPrefix":"Rent ","OriginalPrice":"$7.99","CurrentPrice":"$0.99"}}]}'
        line = lineStart + json + lineEnd
        microsoft.MicrosoftScraper.parseJavascriptLine(line, prod)

        self.assertTrue(len(prod.prices) == 1, 'product should have found one price')
        self.assertEqual(.99, prod.prices[0].amount, 'current price should be .99')
        self.assertEqual(7.99, prod.prices[0].originalAmount, 'original price should be 7.99')
        self.assertTrue(prod.prices[0].isOnSale, 'should recognize sale')

        prod = microsoft.Product('', '', '', [])
        json = '{"SkuDisplayData":{"0001":{"VisibleContent":"Alpha","ScreenReaderOverride":null,"CurrentFormattedPrice":"$7.99","OriginalFormattedPrice":"$8.99"},"0002":{"VisibleContent":"Alpha","ScreenReaderOverride":null,"CurrentFormattedPrice":"$5.99","OriginalFormattedPrice":"$6.99"}}}'
        line = lineStart + json + lineEnd
        microsoft.MicrosoftScraper.parseJavascriptLine(line, prod)

        self.assertTrue(len(prod.prices) == 2, 'product should have found two prices')

        prod = microsoft.Product('', '', '', [])
        json = '{"ProductDisplayData":{"Title":{"VisibleContent":"Test Title"}},"ProductId":"123"}'
        line = lineStart + json + lineEnd
        microsoft.MicrosoftScraper.parseJavascriptLine(line, prod)

        self.assertEqual('Test Title', prod.title)
        self.assertEqual('123', prod.id)

    @mock.patch('HttpTrigger.SharedCode.microsoft.MicrosoftScraper.requestSoupWithRetry', side_effect=mock_requestSoupWithRetry)
    def test_parseMoviePage(self, mock_get):

        def insertMovie(movie):
            insertMovie.callCount += 1
            self.assertTrue(movie != None, 'movie should not be None')

        insertMovie.callCount = 0

        scraper = microsoft.MicrosoftScraper()
        scraper.parseMoviePage('/test/movie', insertMovie)

        self.assertEqual(insertMovie.callCount, 1, "should have found two movies on page")

    @mock.patch('HttpTrigger.SharedCode.microsoft.MicrosoftScraper.requestSoupWithRetry', side_effect=mock_requestSoupWithRetry)
    def test_parseMoviesPage(self, mock_get):
        
        def insertMovie(movie):
            insertMovie.callCount += 1
            self.assertTrue(movie != None, 'movie should not be None')

        insertMovie.callCount = 0

        scraper = microsoft.MicrosoftScraper()
        scraper.parseMoviesPage('/collection/movies', insertMovie)

        self.assertEqual(insertMovie.callCount, 2, "should have found two movies on page")

    @mock.patch('HttpTrigger.SharedCode.microsoft.MicrosoftScraper.requestSoupWithRetry', side_effect=mock_requestSoupWithRetry)
    def test_parseMovies(self, mock_get):

        def insertMovie(movie):
            insertMovie.callCount += 1

        insertMovie.callCount = 0

        scraper = microsoft.MicrosoftScraper()
        scraper.parseMovies(insertMovie)

        self.assertEqual(insertMovie.callCount, 2, "should have found two movies on page")

if __name__ == '__main__':
   unittest.main(TestMicrosoft)