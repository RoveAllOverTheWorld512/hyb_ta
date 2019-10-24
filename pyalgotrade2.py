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
#from pyalgotrade.technical import rsi


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 10000)
        self.__position = None
        self.__instrument = instrument  # 数据导入时命名的sz300748
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # 等待足够的条形图可用于计算SMA。
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        # 如果一个位置没有打开，检查我们是否应该进入一个长位置。
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:   # 股价上穿SMA
                # Enter a buy market order for 10 shares. The order is good till canceled.
                # 输入10股的购买市场订单。订单取消前有效
                # enterLong为买入
                self.__position = self.enterLong(self.__instrument, 100, True)
        # Check if we have to exit the position.
        # 检查我们是否必须离开这个位置。
        # 股价下穿SMA，同时退出指令不处于激活状态，执行卖出
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod):
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("sz300748", "300748.csv")

    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "sz300748", smaPeriod)
    myStrategy.run()
    print(("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()))

for i in range(10, 30):
    run_strategy(i)

