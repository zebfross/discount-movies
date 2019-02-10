import unittest
import HttpTrigger
from unittest import mock
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

class TestMain(unittest.TestCase):

    @mock.patch('HttpTrigger.removeMoviesOlderThanDate', return_value=0)
    @mock.patch('HttpTrigger.insertOrUpdateMovie')
    @mock.patch('HttpTrigger.microsoft.MicrosoftScraper.parseMovies')
    def test_main(self, mock_purge, mockInsert, mockParse):
        HttpTrigger.main(None)

    def test_databaseConnection(self):
        db = HttpTrigger.connectToDatabase()
        self.assertIsNotNone(db, "Database should have connected")

if __name__ == '__main__':
   unittest.main(TestMain)