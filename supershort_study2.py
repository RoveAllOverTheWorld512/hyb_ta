# -*- coding: utf-8 -*-
"""
Created on 2019-10-11 09:12:38

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.class_func import *
from stock_pandas.misc.supershort import *
import sys


def selefirstsignal(df):
    '''
    删除与前一个信号小于2周的重复信号
    '''
#    df = df.sort_index()
    if df.index.name == 'date' and ('date' not in df.columns):
        df = df.reset_index()
    df = df.sort_values(by=['gpdm', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.assign(tmp=df['date']-df['date'].shift(1))
    df.loc[df['gpdm'] != df['gpdm'].shift(1), 'tmp'] = None
    df = df.loc[((df['tmp'] > pd.Timedelta('14 days')) | pd.isnull(df['tmp']))]
    df = df.drop(columns=['tmp'])
    return df


if __name__ == '__main__':
###############################################################################
#    year = 2018
#    csvfn = f'F:\pandas-ta_project\stock_pandas\misc\{year}st2.csv'
#    df = pd.read_csv(csvfn, encoding='GBK')
#    data = []
#    j = 120
#    k = 120
#    n = 60
#    m = 120
#    for i, gpxx in df.iterrows():
#        print(gpxx)
#        filename = gpxx.gpdm[:6]
#        gpmc = gpxx.gpmc
#        date = str(gpxx.date)
#        tdxday = Tdxday(filename)
#        ohlc = tdxday.get_qfqdata(start='20170101')
#        data.append([gpxx.gpdm, gpmc, date] + badnews(ohlc, date, j, k, n, m))
#
#    rs = pd.DataFrame(data,
#                      columns=['gpdm', 'gpmc', 'date',
#                               'date_max', 'days_max', 'close_max', 'zf_max',
#                               'date_1', 'close_1',
#                               'date_min', 'days_min', 'close_min', 'zf_min', 'zf_min_max', 
#                               'date1_max', 'days1_max', 'close1_max', 'zf1_max',
#                               'date2_min', 'days2_min', 'close2_min', 'zf2_min',
#                               'date3_max', 'days3_max', 'close3_max', 'zf3_max'])
#    rs = rs.round(4)
#    rs.to_csv(f'st{year}_{j}_{k}_{n}.csv', encoding='GBK')
#
###############################################################################

#    csvfn = r'F:\pandas-ta_project\sgdf_144_34_21_0.5_-0.3.csv'
#    start = '2019-01-01'
#    end = '2019-12-31'
#    df = pd.read_csv(csvfn, encoding='GBK')
#    df1 = df.loc[(df['date'] >= start) & (df['date'] <= end)]
#    df1 = df1.sort_values(by=['gpdm', 'date'])
#    df2 = df1.drop_duplicates(subset=['gpdm'])
#    df2 = df2.reset_index(drop=True)
##    sys.exit()
#    data = []
#    j = 60
#    k = 30
#    n = 30
#    m = 60
#    ln = len(df2)
#    for i, gpxx in df2.iterrows():
#        print(i, ln, gpxx.gpdm, gpxx.gpmc, gpxx.date)
#        dm = gpxx.gpdm[:6]
#        gpmc = gpxx.gpmc
#        date = gpxx.date
#        tdxday = Tdxday(dm)
#        ohlc = tdxday.get_qfqdata(start='20170101')
#        data.append([gpxx.gpdm, gpmc, date] + badnews(ohlc, date, j, k, n, m))
#
#    rs = pd.DataFrame(data,
#                      columns=['gpdm', 'gpmc', 'date',
#                               'date_max', 'days_max', 'close_max', 'zf_max',
#                               'date_1', 'close_1',
#                               'date_min', 'days_min', 'close_min', 'zf_min', 'zf_min_max', 
#                               'date1_max', 'days1_max', 'close1_max', 'zf1_max',
#                               'date2_min', 'days2_min', 'close2_min', 'zf2_min',
#                               'date3_max', 'days3_max', 'close3_max', 'zf3_max'])
#    rs = rs.round(4)
##    rs.to_csv(f'doublebottom_{j}_{k}_{n}.csv', encoding='GBK')
#    rs.to_csv(f'dou_bott_{start}_{end}_{j}_{k}_{n}.csv', encoding='GBK')

###############################################################################

    csvfn = r'F:\data\sgdf_20170101_20191108_144_55_34_0.4_-0.2.csv'
    start = '2017-01-01'
    end = '2019-12-31'
    df = pd.read_csv(csvfn, encoding='GBK',  parse_dates=True, infer_datetime_format=True)
    df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
    df = selefirstsignal(df)
    df = df.loc[(df['decreasing_34'] < -0.25)]
    df = df.loc[(df['increasing_55'] > 0.50)]
    df = df.reset_index(drop=True)
#    sys.exit()
    
    data = []
    j = 30
    k = 10
    n = 10
    m = 30
    ln = len(df)
    for i, gpxx in df.iterrows():
        print(i, ln, gpxx.gpdm, gpxx.gpmc, gpxx.date)
        dm = gpxx.gpdm[:6]
        gpmc = gpxx.gpmc
        date = gpxx.date.strftime('%Y-%m-%d')
        tdxday = Tdxday(dm)
        ohlc = tdxday.get_qfqdata(start='20170101')
        data.append([gpxx.gpdm, gpmc, date] + supershort(ohlc, date, j, k, n, m))

    rs = pd.DataFrame(data,
                      columns=['gpdm', 'gpmc', 'date',
                               'date_max', 'days_max', 'close_max', 'zf_max',
                               'date_1', 'close_1',
                               'date_min', 'days_min', 'close_min', 'zf_min', 'zf_min_max', 
                               'date1_max', 'days1_max', 'close1_max', 'zf1_max',
                               'date2_min', 'days2_min', 'close2_min', 'zf2_min',
                               'date3_max', 'days3_max', 'close3_max', 'zf3_max'])
    rs = rs.round(4)
#    rs.to_csv(f'doublebottom_{j}_{k}_{n}.csv', encoding='GBK')
    rs.to_csv(f'f:\data\supershort_{start}_{end}_{j}_{k}_{n}.csv', encoding='GBK')
