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
import pandas_ta as ta
import pandas as pd
import datetime
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


def signal(gpdm, start, m1, m, n, in_threshold, de_threshold):
    tdxday = Tdxday(gpdm)
    ohlc = tdxday.get_qfqdata(start=start)
    if ohlc.empty:
        return None
    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n1=n1, n=n,
                         in_threshold=in_threshold, de_threshold=de_threshold)
    try:
        # 新股由于交易天数少，无法计算，会出现没有返回
        # double_bott,double_bott1列的情况
#        signals = ohlc.loc[(ohlc['double_bott'] == 1)]
        signals = ohlc.loc[(ohlc['double_bott1'] == 1)]
    except:
        return None
    if not signals.empty:
        signals = signals.assign(date=signals.index)
        signals = signals.assign(gpdm=tdxday.gpdm)
        signals = signals.assign(gpmc=tdxday.gpmc)
        return dfsortcolumns(signals, subset='gpdm,gpmc,date')
    return None


if __name__ == '__main__':
    now0 = datetime.datetime.now().strftime('%H:%M:%S')
    print('开始运行时间：%s' % now0)    

    tdx = Tdx()
    gpdmb = tdx.get_gpdm()

    sgdf = None
    start = '20160101'    # 股票交易数据起始时间
    m1 = 144   # 上涨时间窗口长度
    m = 34   # 上涨时间窗口长度
    n1 = 55   # 回调时间窗口长度
    n = 21   # 回调时间窗口长度
    # 上面4个参数设定需遵循n+m<=n1,m1远大于m，确保区域叠加
    in_threshold = 0.30  # 上涨幅度阈值
    de_threshold = -0.20  # 回调幅度阈值
    dmb = '''600212.SH
    600393.SH
    600844.SH
    600876.SH
    601872.SH
    603603.SH
    603607.SH
    603936.SH
    000068.SZ
    000532.SZ
    000533.SZ
    000677.SZ
    002209.SZ
    002486.SZ
    002492.SZ
    002524.SZ
    002552.SZ
    002584.SZ
    002786.SZ
    002795.SZ
    002800.SZ
    002947.SZ
    300071.SZ
    300239.SZ
    300306.SZ'''.replace(' ',"").split('\n')
    dmb = [dm[:6] if dm != '' else None for dm in dmb]
    gpdmb = gpdmb.loc[gpdmb['dm'].isin(dmb)]
#    sys.exit()

    k = 0  # 股票代码表起点
    ln = len(gpdmb)   # 股票代码表长度
    for i in range(k, ln):
        row = gpdmb.iloc[i]
        print(i + 1, ln, row.dm, row.gpmc)
        sg = signal(row.dm, start, m1, m, n, in_threshold, de_threshold)
        if isinstance(sg, pd.DataFrame):
            sgdf = pd.concat([sgdf, sg])
        i += 1

    csvfn = f'sgdf_{m1}_{m}_{n}_{in_threshold}_{de_threshold}.csv'
    sgdf.to_csv(csvfn, index=False, encoding='GBK')
    sgdf1 = sgdf.loc[(sgdf.index > '2018-09-01')]
    gpdf = sgdf1[['gpdm', 'gpmc']]
    gpdf = gpdf.drop_duplicates(subset=['gpdm', 'gpmc'])
    gpdf = gpdf.reset_index(drop=True)
    gpdf.to_csv('gpdf_db3.csv', index=False, encoding='GBK')

    sgdf2 = sgdf.loc[(sgdf.index > '2019-10-25')]
    gpdf1 = sgdf2[['gpdm', 'gpmc']]
    gpdf1 = gpdf1.drop_duplicates(subset=['gpdm', 'gpmc'])
    gpdf1 = gpdf1.reset_index(drop=True)
    gpdf1.to_csv('gpdf_db5.csv', index=False, encoding='GBK')

    now1 = datetime.datetime.now().strftime('%H:%M:%S')
    print('开始运行时间：%s' % now0)
    print('开始运行时间：%s' % now1)


#    sys.exit()
#    gpdm = '603936'
#    gpdm = '603936'
#    tdxday = Tdxday(gpdm)
#    ohlc = tdxday.get_qfqdata(start=start)
#    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n1=n1, n=n,
#                         in_threshold=in_threshold, de_threshold=de_threshold)
#    df = dfsortcolumns(ohlc, subset='close')
#    df.to_csv('tmp.csv')