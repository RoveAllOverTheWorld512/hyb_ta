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
from stock_pandas.misc.badnews import *
import pandas_ta as ta
import datetime
import sys


if __name__ == '__main__':
    year = 2018
    csvfn = f'F:\pandas-ta_project\stock_pandas\misc\{year}st2.csv'
    df = pd.read_csv(csvfn, encoding='GBK')
    data = []
    j = 120
    k = 120
    l = 60
    for i, gpxx in df.iterrows():
        print(gpxx)
        filename = gpxx.gpdm[:6]
        gpmc = gpxx.gpmc
        date = str(gpxx.date)
        tdxday = Tdxday(filename)
        ohlc = tdxday.get_qfqdata(start='20170101')
        data.append([gpxx.gpdm, gpmc, date] + badnews(ohlc, date, j, k, l))

    rs = pd.DataFrame(data, columns = ['gpdm', 'gpmc', 'date',
                                       'date_max', 'days_max', 'close_max', 'zf_max',
                                       'date_1', 'close_1',
                                       'date_min', 'days_min', 'close_min', 'zf_min', 'zf_min_max', 
                                       'date1_max', 'days1_max', 'close1_max', 'zf1_max',
                                       'date2_min', 'days2_min', 'close2_min', 'zf2_min',])
    rs = rs.round(4)
    rs.to_csv(f'st{year}_{j}_{k}_{l}.csv', encoding='GBK')
