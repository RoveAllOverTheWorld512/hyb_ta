# -*- coding: utf-8 -*-
"""
Created on 2019-09-29 09:17:25

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
from stock_pandas.misc.gpgm import get_gpmc_fromdb
import pandas_ta as ta
import pandas as pd
import datetime
import time
import sys


def dfsortcolumns(df, subset=None):
    '''
    将df指定的列subset排在最左边
    '''
    if not isinstance(df, pd.DataFrame) or subset is None:
        return df
    if isinstance(subset, str):
        subset = subset.split(',')
    if not isinstance(subset, list):
        return df
    columns = df.columns
    cols = []
    for i in subset:
        if (i in columns) and (i not in cols):
            # 去掉df没有的列或subset指定重复的列
            cols.append(i)
    cols = cols + [i for i in columns if i not in cols]
    return df[cols]


def selefirstsignal(df):
    '''
    删除与前一个信号小于2周的重复信号
    '''
    df = df.sort_index()
    df = df.reset_index()
    df = df.assign(tmp=df['date']-df['date'].shift(1))
    df = df.loc[((df['tmp'] > pd.Timedelta('21 days')) | pd.isnull(df['tmp']))]
    df = df.drop(columns=['tmp'])
    return df.set_index('date')


def signal(gpdm, start, m1, m, n, in_threshold, de_threshold):
    tdxday = Tdxday(gpdm)
    ohlc = tdxday.get_qfqdata(start=start)
    if ohlc.empty:
        return None
    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n1=n1, n=n,
                         in_threshold=in_threshold, de_threshold=de_threshold)
    sc = get_gpfl(gpdm)[0].upper()
    gpdm = f'{gpdm}.{sc}'
    gpmc = get_gpmc_fromdb(gpdm)
    ohlc = pd.merge(ohlc, gpmc, on='date', how='outer')
    ohlc = ohlc.sort_index()
    ohlc['gpmc'].fillna(method='ffill', inplace=True)
    ohlc = ohlc.assign(date=ohlc.index)
    start1 = '20190101'
    ohlc = ohlc.loc[(ohlc['date'] >= start1)]
#    ohlc1 = ohlc.loc[(ohlc['double_bott'] == 1)]

#    ohlc = selefirstsignal(ohlc)
#    if ohlc1.empty:
#        return None
    ohlc = ohlc.assign(gpdm=tdxday.gpdm)
    df = dfsortcolumns(ohlc, subset='gpdm,gpmc,date,close')
    # 注意：df.iloc[-1]返回的是pandas.core.series.Series
    # 下句-1后面有冒号，返回的是pandas.core.frame.DataFrame。“:”不能少，
#    return df.iloc[-1:]

    return df


if __name__ == '__main__':
    now0 = datetime.datetime.now()
    print('开始运行时间：%s' % now0.strftime('%H:%M:%S'))

    tdx = Tdx()
    gpdmb = tdx.get_gpdm()

    start = '20180101'    # 股票交易数据起始时间
    end = datetime.datetime.now().strftime('%Y%m%d')
#    m1 = 144   # 上涨时间窗口长度
#    m = 55   # 上涨时间窗口长度
#    n1 = 89   # 回调时间窗口长度
#    n = 34   # 回调时间窗口长度
#    # 上面4个参数设定需遵循n+m<=n1,m1远大于m，确保区域叠加
#    in_threshold = 0.40  # 上涨幅度阈值
#    de_threshold = -0.25  # 回调幅度阈值

    m1 = 144   # 上涨时间窗口长度
    m = 89   # 上涨时间窗口长度
    n1 = 89   # 回调时间窗口长度
    n = 55   # 回调时间窗口长度
    # 上面4个参数设定需遵循n+m<=n1,m1远大于m，确保区域叠加
    in_threshold = 0.50  # 上涨幅度阈值
    de_threshold = -0.30  # 回调幅度阈值

#    sys.exit()
#    dmb = '''
#    300001.SZ
#    600006.SH
#    600020.SH
#    600048.SH
#    600052.SH
#    600053.SH
#    600069.SH
#    600071.SH
#    600072.SH
#    600075.SH
#    600078.SH
#    600080.SH
#    600081.SH
#    600082.SH
#    600083.SH
#    600084.SH
#    600086.SH
#    600088.SH
#    600093.SH
#    600094.SH
#    600095.SH
#    600097.SH
#    600105.SH
#    600107.SH
#    dmb = '''
#    300001.SZ
#    600112.SH
#    600116.SH'''.replace(' ',"").split('\n')
#    dmb = [dm[:6] if dm != '' else None for dm in dmb]
#    gpdmb = gpdmb.loc[gpdmb['dm'].isin(dmb)]
#    sys.exit()
    gplblst = {'SHZBA': '沪市主板A股',
               'SHKCBA': '沪市科创板A股',
               'SZZBA': '深市主板A股',
               'SZZXBA': '深市中小板A股',
               'SZCYBA': '深市创业板A股'}
    for lb in gplblst:
        start_time = time.time()
        sgdf = None
        gpdmb1 = gpdmb.loc[(gpdmb['gplb'] == gplblst[lb])]
        k = 0  # 股票代码表起点
        ln = len(gpdmb1)   # 股票代码表长度
        for i in range(k, ln):
            row = gpdmb1.iloc[i]
            print(i + 1, ln, row.dm, row.gpmc)
            sg = signal(row.dm, start, m1, m, n, in_threshold, de_threshold)
            if isinstance(sg, pd.DataFrame) and not sg.empty:
                sgdf = pd.concat([sgdf, sg])

            if ((i + 1) % 50 == 0) or (i >= ln - 1):
                now_time = time.time()
                t1 = now_time - start_time
                # 每只股票秒数
                p = t1 / (i - k + 1)
                # 估计剩余时间
                t1 = t1 / 60
                t2 = (ln - i) * p / 60

                print('------已用时%d分钟，估计还需要%d分钟' % (t1, t2))

            i += 1

        if isinstance(sgdf, pd.DataFrame):
            csvfn = f'f:\data\{lb}_{start}_{end}_{m1}_{m}_{n}_{in_threshold}_{de_threshold}.csv'
            sgdf.to_csv(csvfn, index=False, encoding='GBK')
#    sys.exit()
#    sgdf1 = sgdf.loc[(sgdf.index > '2018-09-01')]
#    gpdf = sgdf1[['gpdm', 'gpmc']]
#    gpdf = gpdf.drop_duplicates(subset=['gpdm', 'gpmc'])
#    gpdf = gpdf.reset_index(drop=True)
#    gpdf.to_csv('gpdf_db3.csv', index=False, encoding='GBK')

#    td = (datetime.datetime.now()+datetime.timedelta(-1)).strftime('%Y-%m-%d')
#    now = datetime.datetime.now().strftime('%H%M')
#    sgdf1 = sgdf.loc[(sgdf.index >= td)]
#    gpdf1 = sgdf1.reset_index(drop=True)
#    gpdf1.to_csv(f'f:\data\gp_{m1}_{m}_{n}_{in_threshold}_{de_threshold}_{td}_{now}.csv',
#                 index=False, encoding='GBK')
#
    now1 = datetime.datetime.now()
    print('开始运行时间：%s' % now0)
    print('开始运行时间：%s' % now1.strftime('%H:%M:%S'))
#
#
#    sys.exit()
#    gpdm = '603936'
#    gpdm = '600876'
#    gpdm = '600216'
#    gpdm = '688199'
#    gpdm = '000007'
#    gpdm = '002761'
#    gpdm = '600734'
#    gpdm = '300001'
#    tdxday = Tdxday(gpdm)
#    ohlc = tdxday.get_qfqdata(start=start)
#    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n1=n1, n=n,
#                         in_threshold=in_threshold, de_threshold=de_threshold)
#    df = dfsortcolumns(ohlc, subset='close')
#    from stock_pandas.misc.gpgm import get_gpmc_fromdb
#    sc = get_gpfl(gpdm)[0].upper()
#    gpdm = f'{gpdm}.{sc}'
#    gpmc = get_gpmc_fromdb(gpdm)
#    df1 = pd.merge(df, gpmc, on='date', how='outer')
#    df1 = df1.sort_index()
#    df1.fillna(method='ffill', inplace=True)

#    df = df.loc[(df['double_bott2'] == 1)]
#    df.to_csv(r'f:\data\tmp3.csv')