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
import sys


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

    filename = '002456'
    tdxday = Tdxday(filename)
    ohlc = tdxday.get_qfqdata(start='20170101')
    sys.exit()
    # pybacktest.Backtest通过从python locals()提取交易原始数据
    # pandas DataFrame的名称可以命名为'ohlc', 'bars', 'ohlcv'
    # 数据格式遵循Amibroker的命名约定，date(index)，O(open),H(high),
    # L(low),C(close)
    # 信号Series的名称buy,sell,cover(Boy to Cover),short(Sell Short)
    ohlc = tdxday.get_data_pybacktest(start='20110101')
    ohlc.ta.fractals(high='H', low='L', open='O', close='C', append=True)
    ohlc.ta.bottomreversal(high='H', low='L', open='O', close='C', append=True)
    ohlc.ta.topreversal(high='H', low='L', open='O', close='C', append=True)
    scdm = ohlc.scdm
    ohlc.to_csv(f"{scdm}{filename}.csv")

    # buy买入，sell卖出，Buy to Cover 空单补回，Sell Short 卖空
    # 由于融资融券风险较大，在此不做融券策略，也就是不配置cover和short
    # 只配置buy和sell
    # buy
    buy = ohlc['BOTTOM_REVERSAL']
    sell = ohlc['TOP_REVERSAL']

    # locals() 函数会以字典类型返回当前位置的全部局部变量。
    bt = pybacktest.Backtest(locals(), 'hyb_reversal')
    newlist = list(filter(lambda x: not x.startswith('_'), dir(bt)))
    print(newlist)
    print('\n>  bt.signals\n%s' % bt.signals.tail())
    print('\n>  bt.trades\n%s' % bt.trades.tail())
    print('\n>  bt.positions\n%s' % bt.positions.tail())
    print('\n>  bt.equity\n%s' % bt.equity.tail())
    print('\n>  bt.trade_price\n%s' % bt.trade_price.tail())
    bt.summary()

    fig = plt.figure(figsize=(24, 12))
    ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=3, colspan=4)

    bt.plot_trades(ax=ax1)
    ax1.grid(True)
    plt.ylabel('Price')
    ax1.xaxis.set_visible(False)
    plt.setp(plt.gca().get_xticklabels(), visible=False)

    ax2 = plt.subplot2grid((6, 4), (3, 0), sharex=ax1, rowspan=3, colspan=4)
    plt.xlabel('Date')
    ax2.grid(True)
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(16))
    plt.setp(plt.gca().get_xticklabels(), rotation=45,
             horizontalalignment='right')
    bt.plot_equity(ax=ax2)
    plt.subplots_adjust(left=.09, bottom=.18, right=.94, top=0.94,
                        wspace=.20, hspace=0)
    fig.show()
    fig.savefig('equity_trades.png')
