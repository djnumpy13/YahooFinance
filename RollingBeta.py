import sys
import pandas
from datetime import datetime
from matplotlib import pyplot
from optparse import OptionParser

import YahooDataController
import ConsoleLogger

logger = ConsoleLogger.createLogger()

usage = 'calculates a n-day rolling beta for two assets off of data from yahoo finance'
parser = OptionParser(usage)
parser.add_option('--assetone', help='stock ticker for asset one', dest='assetone', default='SPY', metavar='ticker')
parser.add_option('--assettwo', help='stock ticker for asset two', dest='assettwo', default='GE', metavar='ticker')
parser.add_option('--window', help='n-day rolling window length', dest='rollingwindow', default='30', metavar='num of days')
parser.add_option('--clipped', help='percentage to use for clipping', dest='clippedpct', default='.05', metavar='percentage')
parser.add_option('--start', help='start of time range', dest='start', default='19700101', metavar='%Y%m%d')
parser.add_option('--stop', help='end of time range', dest='stop', default=datetime.now().strftime('%Y%m%d'), metavar='%Y%m%d')
parser.add_option('--outputcsv', help='optional file for writing data', dest='outputcsv', default=None, metavar='filename')
(params, args) = parser.parse_args()

assetone = params.assetone
assettwo = params.assettwo
rollingwindow = int(params.rollingwindow)
clippedpct = float(params.clippedpct)
start = datetime.strptime(params.start, '%Y%m%d')
stop = datetime.strptime(params.stop, '%Y%m%d')
outputcsv = params.outputcsv

logger.info('Message="Logging of startup parameters"; AssetOne="%s"; AssetTwo="%s"; RollingWindow="%s"; ClippedPct="%s"; StartTime="%s"; StopTime="%s";' % (assetone, assettwo, rollingwindow, clippedpct, start, stop))

logger.info('Message="starting retrieval of asset data"')
starttime = datetime.now()

assetonedata = YahooDataController.retrieveData(logger, assetone, start, stop)
assettwodata = YahooDataController.retrieveData(logger, assettwo, start, stop)

calctime = datetime.now() - starttime
logger.info('Message="data retrieval complete."; CalcTime="%s";' % calctime)

if assetonedata is None or assettwodata is None:
    logger.error('Message="Data missing for at least one asset. exiting gracefully..."')
    sys.exit(1)

logger.info('Message="starting normalization of asset data"')
starttime = datetime.now()

logger.info('Message="Combining data frames and handling missing days"')
data = pandas.concat([assetonedata, assettwodata], axis=1, keys=[assetone, assettwo])
data = data.dropna()
logger.info('Message="length of data frame after dropping incomplete days is %s"' % len(data.index))

calctime = datetime.now() - starttime
logger.info('Message="data normalization complete."; CalcTime="%s";' % calctime)

logger.info('Message="starting rolling beta calculation."')
starttime = datetime.now()

dailypctchange = data / data.shift(1) - 1
rollingvar = pandas.rolling_var(dailypctchange[(assetone, 'Close')], window=rollingwindow)
rollingcov = pandas.rolling_cov(dailypctchange[(assetone, 'Close')], dailypctchange[(assettwo, 'Close')], window=rollingwindow)
rollingbeta = rollingcov / rollingvar
rollingbeta = rollingbeta.dropna()

calctime = datetime.now() - starttime
logger.info('Message="rolling beta calculation complete."; CalcTime="%s"; Window="%s";' % (calctime, rollingwindow) )

logger.info('Message="starting rolling beta calculation with clipping"; ClipPct="%s"' % clippedpct)
starttime = datetime.now()

clippeddailypctchange = dailypctchange.clip(lower=-clippedpct, upper=clippedpct)
clippedrollingvar = pandas.rolling_var(clippeddailypctchange[(assetone, 'Close')], window=rollingwindow)
clippedrollingcov = pandas.rolling_cov(clippeddailypctchange[(assetone, 'Close')], clippeddailypctchange[(assettwo, 'Close')], window=rollingwindow)
clippedrollingbeta = clippedrollingcov / clippedrollingvar
clippedrollingbeta = clippedrollingbeta.dropna()

calctime = datetime.now() - starttime
logger.info('Message="rolling beta calculation with clipping complete."; CalcTime="%s"; Window="%s"; ClippedPct="%s";' % (calctime, rollingwindow, clippedpct))

if outputcsv is not None:
    logger.info('Message="writing output beta values to file %s";' % outputcsv)
    rollingbeta.to_csv(outputcsv)

logger.info('Message="plotting all of the results using matplotlib..."')

(figure, axes) = pyplot.subplots(nrows=3, ncols=2)

assetoneplot = data[(assetone, 'Close')].plot(ax=axes[0,0])
assetoneplot.set_title('Historical prices for %s' % assetone)
assettwoplot = data[(assettwo, 'Close')].plot(ax=axes[0,1])
assettwoplot.set_title('Historical prices for %s' % assettwo)

returnsoneplot = dailypctchange[(assetone, 'Close')].hist(ax=axes[1,0], bins=50)
returnsoneplot.set_title('Histogram of daily returns for %s' % assetone)
returnstwoplot = dailypctchange[(assettwo, 'Close')].hist(ax=axes[1,1], bins=50)
returnstwoplot.set_title('Histogram of daily returns for %s' % assettwo)

betaplot = rollingbeta.plot(ax=axes[2,0])
betaplot.set_title(r'%s day rolling $\beta$ between %s and %s (no outlier correction)' % (rollingwindow, assetone, assettwo))
ylimmax = rollingbeta.abs().max()
betaplot.set_ylim([-ylimmax, ylimmax])
clippedbetaplot = clippedrollingbeta.plot(ax=axes[2,1])
clippedbetaplot.set_title(r'%s day rolling $\beta$ between %s and %s (daily returns clipped at %s)' % (rollingwindow, assetone, assettwo, clippedpct))
clippedbetaplot.set_ylim([-ylimmax, ylimmax])

pyplot.show()
