# -*- coding: utf-8 -*-
"""
Created on 2019-10-11 09:12:38

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pybacktest
import matplotlib.dates as mdates
import mpl_finance as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta
import datetime


def extract_frame(dataobj):
    '''
    提取数据帧,从
    '''
    df = {}
    ext_mask = ('buyprice', 'sellprice', 'shortprice', 'coverprice')
    int_mask = ('BuyPrice', 'SellPrice', 'ShortPrice', 'CoverPrice')
#    list(zip(int_mask, ext_mask))
#    [('Buy', 'buy'), ('Sell', 'sell'), ('Short', 'short'), ('Cover', 'cover')]
    for f_int, f_ext in zip(int_mask, ext_mask):
        obj = dataobj.get(f_ext)
        if isinstance(obj, pd.Series):
            df[f_int] = obj
        else:
            df[f_int] = None
    if any([isinstance(x, pd.Series) for x in list(df.values())]):
        return pd.DataFrame(df)
    return None


if __name__ == '__main__':
    filename = '600674'
    tdxday = Tdxday(filename)
    ohlc = tdxday.get_data_pybacktest(start='20180101')

    short_ma = 10
    long_ma = 60

    ms = ohlc['C'].rolling(short_ma).mean()
    ml = ohlc['C'].rolling(long_ma).mean()

    # buy买入，sell卖出，cover，Short sell做空 
    buy = (ms > ml) & (ms.shift() < ml.shift())  # ma cross up
    sell = (ms < ml) & (ms.shift() > ml.shift())  # ma cross down
#    buy = cover = (ms > ml) & (ms.shift() < ml.shift())  # ma cross up
#    sell = short = (ms < ml) & (ms.shift() > ml.shift())  # ma cross down

    # 

    print('>  Short MA\n%s\n' % ms.tail())
    print('>  Long MA\n%s\n' % ml.tail())
    print('>  Buy/Cover signals\n%s\n' % buy.tail())
    print('>  Short/Sell signals\n%s\n' % sell.tail())

    #locals() 函数会以字典类型返回当前位置的全部局部变量。
    bt = pybacktest.Backtest(locals(), 'ma_cross')
    newlist = list(filter(lambda x: not x.startswith('_'), dir(bt)))
    print(newlist)
    print('\n>  bt.signals\n%s' % bt.signals.tail())
    print('\n>  bt.trades\n%s' % bt.trades.tail())
    print('\n>  bt.positions\n%s' % bt.positions.tail())
    print('\n>  bt.equity\n%s' % bt.equity.tail())
    print('\n>  bt.trade_price\n%s' % bt.trade_price.tail())
    bt.summary()
    
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111)
    bt.plot_equity(ax=ax)
#    bt.plot_trades(ax=ax)