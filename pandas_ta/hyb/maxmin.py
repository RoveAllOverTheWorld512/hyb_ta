# -*- coding: utf-8 -*-
"""
Created on 2019-10-21 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

maxmin计算最大值最小值

"""

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__))))


import pandas as pd
from numpy import NaN as npNaN
from math import isnan
from pandas_ta.utils import verify_series


def maxmin(close, maxset=[8, 13, 21, 34, 55, 89, 144, 233], minset=[8, 13, 21, 34, 55, 89, 144, 233], **kwargs):
    '''

    '''
    def idxmax(ds, i, j):
        '''
        返回pandas.Series指定位置i、指定区间内j的最大值及索引
        返回的是pandas.Series，只有一行，当有多个相同最大值时
        返回的是前面的那个
        注意：ds索引号为顺序号，j>0
        '''
        if isnan(i):
            return None
        if (j <= 0) | ((i - j + 1) < 0) | (i > len(ds)):
            return None
        s = ds.iloc[(i - j + 1): i + 1]
        return s.loc[[s.idxmax()]]

    def idxmin(ds, i, j):
        '''
        返回pandas.Series指定位置i、指定区间内j的最小值及索引
        返回的是pandas.Series，只有一行，当有多个相同最小值时
        返回的是前面的那个
        注意：ds索引号为顺序号，j>0
        '''
        if isnan(i):
            return None
        if (j <= 0) | ((i - j + 1) < 0) | (i > len(ds)):
            return None
    #    print(f'i={i}')
        s = ds.iloc[(i - j + 1): i + 1]
        return s.loc[[s.idxmin()]]

    def hhv(ds, n):
        '''
        返回pandas.Series前n周期的最大值、对应日期、相隔交易日数、跌幅
        '''
        indexname = ds.index.name  # 索引名
        name = ds.name  # 列名
        df1 = ds.reset_index()  # 变成了pd.DataFrame,索引为pd.RangeIndex，原索引变成列date
    
        ds2 = df1[name]  # 索引为pd.RangeIndex
        # n天内高点
        try:
            ds3 = pd.concat([idxmax(ds2, i, n) for i in range(len(ds2))])
            # 由于前面n-1行没有返回数据,索引ds3的长度要比ds2对n-1
            df3 = ds3.reset_index()  # 将原索引变成一列index
            dt = df1[indexname].iloc[df3['index']].to_frame()  # 注意其索引
            dt = dt.reset_index(drop=True)
            df3['idxmaxdate'] = dt['date']
            df3.index += (n - 1)  # 由于前面n-1行没有返回数据，将所以往后移n-1
            df1['max'] = df3[name]  # 前n周期最大值
            df1['idxmax'] = df3['index']  # 最大值对应的索引序号
            df1['maxdate'] = df3['idxmaxdate'].map(lambda x: x.strftime('%Y-%m-%d'))
            df1['h_days'] = df1.index - df1['idxmax']  # 相隔交易日数
            df1['down'] = df1['close']/df1['max'] - 1  # 跌幅
        except:
            # 对于交易数据天数少的情况
            df1['max'] = npNaN  # 前n周期最大值
            df1['maxdate'] = npNaN  # 对应日期
            df1['h_days'] = npNaN  # 间隔交易日数
            df1['down'] = npNaN  # 跌幅
    
        df = df1.set_index(indexname)
        df = df[['maxdate', 'max', 'h_days', 'down']]
    
        df = df.rename(columns={'max': f'max_{n}',
                                'maxdate': f'maxdate_{n}',
                                'h_days': f'h_days_{n}',
                                'down': f'down_{n}'})
    
        return df

    def llv(ds, n):
        '''
        返回pandas.Series前n周期的最大值、对应日期、相隔交易日数、跌幅
        '''
        indexname = ds.index.name  # 索引名
        name = ds.name  # 列名
        df1 = ds.reset_index()  # 变成了pd.DataFrame,索引为pd.RangeIndex，原索引变成列date
    
        ds2 = df1[name]  # 索引为pd.RangeIndex
        # n天内高点
        try:
            ds3 = pd.concat([idxmin(ds2, i, n) for i in range(len(ds2))])
            # 由于前面n-1行没有返回数据,索引ds3的长度要比ds2对n-1
            df3 = ds3.reset_index()  # 将原索引变成一列index
            dt = df1[indexname].iloc[df3['index']].to_frame()  # 注意其索引
            dt = dt.reset_index(drop=True)
            df3['idxmindate'] = dt['date']
            df3.index += (n - 1)  # 由于前面n-1行没有返回数据，将所以往后移n-1
            df1['min'] = df3[name]  # 前n周期最大值
            df1['idxmin'] = df3['index']  # 最大值对应的索引序号
            df1['mindate'] = df3['idxmindate'].map(lambda x: x.strftime('%Y-%m-%d'))
            df1['l_days'] = df1.index - df1['idxmin']  # 相隔交易日数
            df1['up'] = df1['close']/df1['min'] - 1  # 跌幅
        except:
            # 对于交易数据天数少的情况
            df1['min'] = npNaN  # 前n周期最大值
            df1['mindate'] = npNaN  # 对应日期
            df1['l_days'] = npNaN  # 间隔交易日数
            df1['up'] = npNaN  # 跌幅
    
        df = df1.set_index(indexname)
        df = df[['mindate', 'min', 'l_days', 'up']]
    
        df = df.rename(columns={'min': f'min_{n}',
                                'mindate': f'mindate_{n}',
                                'l_days': f'l_days_{n}',
                                'up': f'up_{n}'})
    
        return df


    # Validate Arguments
    close = verify_series(close)

    # 上涨窗口和回调窗口长度
        
    ds = close  # 应该为pd.Series,索引为pd.DatetimeIndex
    df = ds.to_frame()  # 变成了pd.DataFrame
    for n in maxset:
        df1 = hhv(ds, n)
        df = df.join(df1)

    for n in minset:
        df1 = llv(ds, n)
        df = df.join(df1)

#    df = df.drop(columns=[name])

    return df

maxmin.__doc__ = \
    '''

    思路：假定股价经过较长时间的盘整，近期拉升，最近回调。通过查找n天内和n1天内的高点
    如果两个高点重合，即确定该高点为近期高点（位置idxmax）。再从idxmax往前查找m天内和
    m1天内点近远两个低点（idxmin,idxmin1），
    '''

if __name__ == '__main__':
    from stock_pandas.tdx.tdxdayread import Tdxday
    from stock_pandas.tdx.class_func import *
    gpdm = '600734'
    start = '20180101'
    tdxday = Tdxday(gpdm)
    ohlc = tdxday.get_qfqdata(start=start)
    
    close = ohlc.close
    df = maxmin(ohlc.close)
 