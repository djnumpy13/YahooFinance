import logging
import pandas
import sys
import urllib
from datetime import datetime

YAHOOURL = 'http://ichart.finance.yahoo.com/table.csv?s=%(s)s&a=%(a)s&b=%(b)s&c=%(c)s&d=%(d)s&e=%(e)s&f=%(f)s&g=d&ignore=.csv'

def retrieveData(logger, asset, fromdate, todate):

    logger.info('Message="Retrieving data from yahoo"; Asset="%s"; FromDate="%s"; ToDate="%s";' % (asset, fromdate.strftime('%Y%m%d'), todate.strftime('%Y%m%d')))

    params = dict()
    params['s'] = asset

    params['a'] = fromdate.strftime('%m') 
    params['b'] = fromdate.strftime('%d')
    params['c'] = fromdate.strftime('%Y')

    params['d'] = todate.strftime('%m')
    params['e'] = todate.strftime('%d')
    params['f'] = todate.strftime('%Y')

    dataurl = YAHOOURL % params

    try:
        f = urllib.urlopen(dataurl)
    except IOError as e:
        logger.error('Message="Urllib has returned an io exception"; URL="%s";' % dataurl)
        sys.exit(1)

    if f is not None:
        try:
            data = pandas.read_csv(f)
            data.index = pandas.to_datetime(data.pop('Date'))
            data.sort(inplace = True)
            logger.info('Message="Successfully retrieved data from Yahoo"; Asset="%s"; DataPoints="%s";' % (asset, len(data.index)))
            return data
        except pandas._parser.CParserError as e:
            logger.warn('Message="Pandas error converting csv to DataFrame. Returning None')

    return None
