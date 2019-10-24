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

def signal(gpdm):
    tdxday = Tdxday(gpdm)
    start = '20170101'
    ohlc = tdxday.get_qfqdata(start=start)
    if ohlc.empty:
        return None
    ohlc.ta.bottompattern(append=True)
    signals = ohlc.loc[(ohlc['BOTTOM_REVERSAL']==1)]
    if not signals.empty:
        signals['date'] = signals.index
        signals['gpdm'] = tdxday.gpdm
        signals['gpmc'] = tdxday.gpmc
        return signals[['date', 'gpdm', 'gpmc']]
    return None
    
if __name__ == '__main__':

    tdx = Tdx()
    gpdmb = tdx.get_gpdm()
    
    sgdf = pd.DataFrame(columns=['date', 'gpdm', 'gpmc'])
    n = 0
    m = len(gpdmb)

    for i in range(n, m):
        row = gpdmb.iloc[i]
        print(i+1, m,row.dm, row.gpmc)
        sg = signal(row.dm)
        if isinstance(sg, pd.DataFrame):
            sgdf = sgdf.append(sg)
        i += 1

    sgdf.to_csv('sgdf.csv', index=False ,encoding='GBK')
    sgdf1=sgdf.loc[(sgdf.index>'2018-01-01')]
    gpdf = sgdf1[['gpdm', 'gpmc']]
    gpdf = gpdf.drop_duplicates(subset=['gpdm', 'gpmc'])
    gpdf = gpdf.reset_index(drop=True)

    gpdf.to_csv('gpdf.csv', index=False ,encoding='GBK')
    
        