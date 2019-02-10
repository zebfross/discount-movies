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

def removeMoviesOlderThanDate(db, newDate):
    result = db.movies.delete_many({"date_updated": {"$lt": newDate}})
    return result.deleted_count

def insertOrUpdateMovie(db, movie):
    db.movies.update_one({"id": movie["id"]}, {'$set': movie}, True) # inserts if doesn't already exist

def connectToDatabase():
    try:
        username = os.environ['MOVIES_DB_UNAME']
        password = os.environ['MOVIES_DB_PSWD']
        mongo = MongoClient('mongodb://' + username + ':' + password + '@ds028559.mlab.com:28559/discount-movies')
        db = mongo['discount-movies']
        return db
    except Exception as e:
        utils.log().exception("Error connecting to database")
        return None


def main(req: func.HttpRequest) -> func.HttpResponse:
    utils.log().debug('received request')

    newDateUpdated = datetime.datetime.utcnow()
    db = connectToDatabase()
    if db is None:
        return fail(f"Error connecting to database", 500)
    
    moviesFound = []
    def insertMovie(movie):
        nonlocal db
        nonlocal moviesFound
        try:
            utils.log().info("inserting/updating movie")
            movie["date_updated"] = newDateUpdated
            insertOrUpdateMovie(db, movie)
            moviesFound.append(movie)
        except Exception as e:
            utils.log().exception("Error inserting movie into database")

    microsoftScraper = microsoft.MicrosoftScraper()
    microsoftScraper.parseMovies(insertMovie)

    numRemoved = removeMoviesOlderThanDate(db, newDateUpdated)
    utils.log().info('parsing successful.  Deleted %d movies', numRemoved)
    return func.HttpResponse("parsing successful.  Deleted " + str(numRemoved) + " movies")
    
if __name__ == "__main__":
    main(None)