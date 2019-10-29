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


def signal(gpdm, start, m1, m, n, in_threshold, de_threshold):
    tdxday = Tdxday(gpdm)
    ohlc = tdxday.get_qfqdata(start=start)
    if ohlc.empty:
        return None
#    ohlc.ta.doublebottom(append=True, m=34, n=21, in_threshold=0.35, de_threshold=-0.2)
#    ohlc.ta.doublebottom(append=True, m=m, n=n,
#                         in_threshold=in_threshold, de_threshold=de_threshold)
    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n=n,
                         in_threshold=in_threshold, de_threshold=de_threshold)
    try:
        # 新股由于交易天数少，无法计算，会出现没有返回
        # double_bott的情况
#        signals = ohlc.loc[(ohlc['double_bott'] == 1)]
        signals = ohlc.loc[(ohlc['double_bott1'] == 1)]
    except:
        return None
    if not signals.empty:
        signals['date'] = signals.index
        signals['gpdm'] = tdxday.gpdm
        signals['gpmc'] = tdxday.gpmc
        return signals[['date', 'gpdm', 'gpmc']]
    return None


if __name__ == '__main__':
    now0 = datetime.datetime.now().strftime('%H:%M:%S')
    print('开始运行时间：%s' % now0)    

    tdx = Tdx()
    gpdmb = tdx.get_gpdm()

    sgdf = pd.DataFrame(columns=['date', 'gpdm', 'gpmc'])
    start = '20180101'    # 股票交易数据起始时间
    m1 = 121   # 上涨时间窗口长度
    m = 55   # 上涨时间窗口长度
    n = 21   # 回调时间窗口长度
    in_threshold = 0.30  # 上涨幅度阈值
    de_threshold = -0.15  # 回调幅度阈值
    k = 0  # 股票代码表起点
    ln = len(gpdmb)   # 股票代码表长度
#    sys.exit()

    for i in range(k, ln):
        row = gpdmb.iloc[i]
        print(i + 1, ln, row.dm, row.gpmc)
        sg = signal(row.dm, start, m1, m, n, in_threshold, de_threshold)
        if isinstance(sg, pd.DataFrame):
            sgdf = sgdf.append(sg)
        i += 1

    csvfn = f'sgdf_{m1}_{m}_{n}.csv'
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
#    gpdm = '600485'
#    tdxday = Tdxday(gpdm)
#    ohlc = tdxday.get_qfqdata(start=start)
#    ohlc.ta.doublebottom(append=True, m1=m1, m=m, n=n,
#                         in_threshold=in_threshold, de_threshold=de_threshold)
