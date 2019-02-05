import unittest
import HttpTrigger
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

class TestMain(unittest.TestCase):

    @mock.patch('HttpTrigger.SharedCode.microsoft.MicrosoftScraper.requestSoupWithRetry', side_effect=mock_requestSoupWithRetry)
    @mock.patch('HttpTrigger.removeMoviesOlderThanDate', return_value=0)
    @mock.patch('HttpTrigger.insertOrUpdateMovie')
    def test_main(self, mock_get, mock_purge, mockInsert):
        HttpTrigger.main(None)

if __name__ == '__main__':
   unittest.main(TestMain)