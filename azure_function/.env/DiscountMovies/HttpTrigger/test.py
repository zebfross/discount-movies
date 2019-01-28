import azure.functions as func
import os
import json
import sys
import logging
import datetime
from bs4 import BeautifulSoup as bs
from urllib.request import (
    urlopen, urlparse, urlunparse, urlretrieve, Request)
import re
from SharedCode import microsoft
from SharedCode import utils
from pymongo import MongoClient

def fail(msg, code):
    logging.exception(msg)
    logging.shutdown()

def main():
    #utils.initLogging(logging.INFO, logging.DEBUG)
    #parseJavascriptLine('{'"InitialSkus")
    #parseJavascriptLine('parseJavascriptLine', '')
    #parseMoviePage('/en-us/store/p/halloween-h20-20-years-later/8d6kgwzl5f1b', '')
    #parseMoviePage('/en-us/store/p/todd-mcfarlanes-spawn/8d6kgwzl68v1', '8d6kgwzl68v1')
    #parseMoviePage('/en-us/store/p/quarantine-2-terminal/8d6kgwzl5r9p', '8d6kgwzl5r9p')
    #products = parseMoviesPage('/en-us/store/movies-and-tv/collection/sales-specials/fh_store_landing_page_fc1')
    
    def insertMovie(movie):
        utils.log().info('inserted movie!')

    microsoft.parseMovies(insertMovie)
    #logger = utils.log()
    #logger.info('test %s', 'test')
    #logger.debug('test debug')
    #logger.info('test info')
    #logger.warning('test warning')
    #logger.error('test error')

    logging.shutdown()

if __name__ == "__main__":
    main()