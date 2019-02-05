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

def removeMoviesOlderThanDate(moviesTable, newDate):
    result = moviesTable.delete_many({"date_updated": {"$lt": newDate}})
    return result.deleted_count

def insertOrUpdateMovie(moviesTable, movie):
    moviesTable.update_one({"id": movie["id"]}, {'$set': movie}, True) # inserts if doesn't already exist


def main(req: func.HttpRequest) -> func.HttpResponse:
    utils.log().debug('received request')

    newDateUpdated = datetime.datetime.utcnow()

    try:
        mongo = MongoClient('mongodb://root:zebfross1@ds028559.mlab.com:28559/discount-movies')
        db = mongo['discount-movies']
        moviesTable = db.movies
    except Exception as e:
        return fail(f"Error connecting to database", 500)
    
    moviesFound = []
    def insertMovie(movie):
        nonlocal moviesTable
        nonlocal moviesFound
        try:
            utils.log().info("inserting/updating movie")
            movie["date_updated"] = newDateUpdated
            insertOrUpdateMovie(moviesTable, movie)
            moviesFound.append(movie)
        except Exception as e:
            utils.log().exception("Error inserting movie into database")

    microsoftScraper = microsoft.MicrosoftScraper()
    microsoftScraper.parseMovies(insertMovie)

    numRemoved = removeMoviesOlderThanDate(moviesTable, newDateUpdated)
    utils.log().info('parsing successful.  Deleted %d movies', numRemoved)
    return func.HttpResponse("parsing successful.  Deleted " + str(numRemoved) + " movies")
    
if __name__ == "__main__":
    main(None)