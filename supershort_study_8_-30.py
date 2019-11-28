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
import os
import datetime
import time


def selefirstsignal(df):
    '''
    删除与前一个信号小于3周的重复信号
    '''
#    df = df.sort_index()
    if df.index.name == 'date' and ('date' not in df.columns):
        df = df.reset_index()
    df = df.sort_values(by=['gpdm', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.assign(tmp=df['date']-df['date'].shift(1))
    df.loc[df['gpdm'] != df['gpdm'].shift(1), 'tmp'] = None
    df = df.loc[((df['tmp'] > pd.Timedelta('21 days')) | pd.isnull(df['tmp']))]
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
    df = None
    start = '2018-01-01'
    end = (datetime.datetime.now() - datetime.timedelta(5)).strftime('%Y-%m-%d')
    gplblst = {'SHZBA': '沪市主板A股',
               'SHKCBA': '沪市科创板A股',
               'SZZBA': '深市主板A股',
               'SZZXBA': '深市中小板A股',
               'SZCYBA': '深市创业板A股'}
    for lb in gplblst:
#        csvfn = f'f:\data\{lb}_20180101_20191122_144_89_55_0.5_-0.3.csv'
        csvfn = f'f:\data\{lb}_20181001_20191124_89_55_8_0.5_-0.3.csv'
        if os.path.exists(csvfn):
            df1 = pd.read_csv(csvfn, encoding='GBK',  parse_dates=True, infer_datetime_format=True)
            df1 = df1.loc[(df1['double_bott'] == 1)]
            df1 = selefirstsignal(df1)
            df1 = df1.loc[(df1['date'] >= start) & (df1['date'] <= end)]
            df = pd.concat([df, df1])

    df = df.reset_index(drop=True)

#    df = df.loc[(df['decreasing_34'] < -0.25)]
#    df = df.loc[(df['increasing_55'] > 0.50)]
#    df = selefirstsignal(df)

#    sys.exit()
    
    data = []
    j = 30
    k = 20
    n = 20
    m = 60
    ln = len(df)
    start_time = time.time()
    for i, gpxx in df.iterrows():
        print(i, ln, gpxx.gpdm, gpxx.gpmc, gpxx.date)
        dm = gpxx.gpdm[:6]
        gpmc = gpxx.gpmc
        date = gpxx.date.strftime('%Y-%m-%d')
        tdxday = Tdxday(dm)
        ohlc = tdxday.get_qfqdata(start='20160101')
        data.append([gpxx.gpdm, gpmc, date] + supershort(ohlc, date, j, k, n, m))

        if ((i + 1) % 50 == 0) or (i >= ln - 1):
            now_time = time.time()
            t1 = now_time - start_time
            # 每只股票秒数
            p = t1 / (i - k + 1)
            # 估计剩余时间
            t1 = t1 / 60
            t2 = (ln - i) * p / 60

            print('------已用时%d分钟，估计还需要%d分钟' % (t1, t2))


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
#    rs.to_csv(f'f:\data\supershort__89_55_0.5_-0.3_{start}_{end}_{j}_{k}_{n}_{m}.csv', encoding='GBK')
    rs.to_csv(f'f:\data\supershort_8_-0.3_{start}_{end}_{j}_{k}_{n}_{m}.csv', encoding='GBK')
