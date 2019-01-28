import re
import logging

def currencyToFloat(currency):
    if currency is "":
        return 0

    try:
        if not currency:
            return 0
        elif "$" in currency:
            return float(re.sub("\$", "", currency))
        else:
            return float(currency)
    except:
        log().error('could not convert currency: ' + currency)
        return 0

def cleanString(text):
    result = re.sub('\x01..', '', text)
    
    return result

logger = None

def log():
    global logger
    if logger is None:
        logger = logging.getLogger('DiscountMovies')
        logger.setLevel(logging.DEBUG) #By default, logs all messages

        consoleHandler = logging.StreamHandler() #StreamHandler logs to console
        consoleHandler.setLevel(logging.INFO)
        consoleFormat = logging.Formatter('%(levelname)s: %(message)s')
        consoleHandler.setFormatter(consoleFormat)
        logger.addHandler(consoleHandler)

        fileHandler = logging.FileHandler("info.log", mode='w')
        fileHandler.setLevel(logging.DEBUG)
        fileFormat = logging.Formatter('%(asctime)s | %(lineno)-4d | %(levelname)-8s| %(message)s')
        fileHandler.setFormatter(fileFormat)
        logger.addHandler(fileHandler)

    return logger
