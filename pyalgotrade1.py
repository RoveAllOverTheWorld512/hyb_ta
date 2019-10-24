# -*- coding: utf-8 -*-
"""
Created on 2019-10-10 15:12:45

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.__rsi = rsi.RSI(feed[instrument].getCloseDataSeries(), 14)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info("%s %s %s" % (bar.getClose(), self.__rsi[-1], self.__sma[-1]))

# Load the yahoo feed from the CSV file
feed = yahoofeed.Feed()
feed.addBarsFromCSV("sz300748", "300748.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, "sz300748")
myStrategy.run()