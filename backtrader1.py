# -*- coding: utf-8 -*-
"""
Created on 2019-10-12 18:59:39

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

#基于macd技术指标的策略
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
 
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd
#import statsmodel as sm
# Import the backtrader platform
import backtrader as bt
# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
    )
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
 
    def __init__(self):
        self.dataclose_x = self.datas[0].close
        self.dataclose_y = self.datas[1].close
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def notify_cashvalue(self, cash, value):
        self.log('Cash %s Value %s' % (cash, value))
    def notify_order(self, order):
        print(type(order), 'Is Buy ', order.isbuy())
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
 
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
 
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
 
            self.bar_executed = len(self)
 
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
 
        self.order = None
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
 
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
 
    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose_x[0])
        self.log('Close, %.2f' % self.dataclose_y[0])
        # Check if we are in the market
        if not self.getposition(self.datas[1]):
 
            # Not yet ... we MIGHT BUY if ...
            if self.macd[0]>self.macd[-1]:
                    #if sma[0]<top[-5]:
                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE,{},{}'.format(self.dataclose_y[0],self.dataclose_x[0]) )
 
                        # Keep track of the created order to avoid a 2nd order
                        self.order=self.sell(self.datas[1])
                        #self.order = self.buy(self.datas[0])
                        
 
        else:
 
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('BUY CREATE,{},{}'.format(self.dataclose_y[0],self.dataclose_x[0]) )
 
                # Keep track of the created order to avoid a 2nd order
                self.log('Pos size %s' % self.position.size)
                self.order = self.close(self.datas[1])
                #self.order = self.close(self.datas[0])
        
                
 
if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    datapath_1='sz000651.csv'
    datapath_2='sz300748.csv'
    # Create a Data Feed
    data_1 = bt.feeds.GenericCSVData(
        dataname=datapath_1,
        # Do not pass values before this date
        fromdate=datetime.datetime(2018, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2019, 9, 30),
        dtformat=('%Y-%m-%d'),
        tmformat=('%H.%M.%S'),
        date=0,
        open=1,
        close=2,
        high=3,
        low=4,
        volume=5,
        openinterest=6,
        code=-1,
        reverse=False)
    data_2 = bt.feeds.GenericCSVData(
        dataname=datapath_2,
        # Do not pass values before this date
        fromdate=datetime.datetime(1991, 12, 23),
        # Do not pass values after this date
        todate=datetime.datetime(2017, 12, 31),
        dtformat=('%Y-%m-%d'),
        tmformat=('%H.%M.%S'),
        date=0,
        open=1,
        close=2,
        high=3,
        low=4,
        volume=5,
        openinterest=6,
        reverse=False)
 
    # Add the Data Feed to Cerebro
    cerebro.adddata(data_1)
    cerebro.adddata(data_2)
 
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100) 
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
 
    # Run over everything
    cerebro.run()
 
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
#    cerebro.plot()