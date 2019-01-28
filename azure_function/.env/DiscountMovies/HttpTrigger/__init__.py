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
from .SharedCode import microsoft
from .SharedCode import utils
from pymongo import MongoClient

def fail(msg, code) -> func.HttpResponse:
    utils.log().exception(msg)
    return func.HttpResponse(msg, status_code=code)

def main(req: func.HttpRequest) -> func.HttpResponse:
    utils.log().debug('received request')
    #parseJavascriptLine('{'"InitialSkus")
    #parseJavascriptLine('parseJavascriptLine', '')
    #parseMoviePage('/en-us/store/p/halloween-h20-20-years-later/8d6kgwzl5f1b', '')
    #parseMoviePage('/en-us/store/p/todd-mcfarlanes-spawn/8d6kgwzl68v1', '8d6kgwzl68v1')
    #parseMoviePage('/en-us/store/p/quarantine-2-terminal/8d6kgwzl5r9p', '8d6kgwzl5r9p')
    #products = parseMoviesPage('/en-us/store/movies-and-tv/collection/sales-specials/fh_store_landing_page_fc1')

    newDateUpdated = datetime.datetime.utcnow()

    try:
        mongo = MongoClient('mongodb://root:zebfross1@ds028559.mlab.com:28559/discount-movies')
        db = mongo['discount-movies']
        moviesTable = db.movies
    except Exception as e:
        return fail(f"Error connecting to database", 500)
    
    def insertMovie(movie):
        nonlocal moviesTable
        try:
            utils.log().info("inserting/updating movie")
            movie["date_updated"] = newDateUpdated
            moviesTable.update_one({"id": movie["id"]}, {'$set': movie}, True) # inserts if doesn't already exist
        except Exception as e:
            utils.log().exception("Error inserting movie into database")

    microsoft.parseMovies(insertMovie)

    #numRemoved = 0
    result = moviesTable.delete_many({"date_updated": {"$lt": newDateUpdated}})
    utils.log().info('parsing successful.  Deleted %d movies', result.deleted_count)
    return func.HttpResponse('parsing successful.  Deleted ' + str(result.deleted_count) + ' movies')
    
if __name__ == "__main__":
    main(None)