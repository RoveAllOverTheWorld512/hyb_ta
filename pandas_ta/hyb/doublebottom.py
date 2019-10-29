# -*- coding: utf-8 -*-
"""
Created on 2019-10-21 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

double bottom pattern双底形态研究

"""

import pandas as pd
from numpy import NaN as npNaN
from math import isnan
from ..utils import verify_series


def doublebottom(open, high, low, close, m1=None, m=None, n=None, **kwargs):
    '''
    双底形态研究：研究最长m+n窗口内上涨回调的情况。尽管取名是双底研究，不一定
    是双底，也可能是上涨趋势中的回调。
    m1:近期高点前查找低点的窗口长度
    m:近期高点前查找低点的窗口长度
    n:近期查找高点的窗口长度
    in_threshold:涨幅阈值，为正值
    de_threshold:回调跌幅阈值，为负值
    '''
    def idxmax(ds, i, j):
        '''
        返回pandas.Series指定位置、指定区间内的最大值及索引
        返回的是pandas.Series，只有一行，当有多个相同最大值时
        返回的是前面的那个
        注意：ds索引号为顺序号，l>0
        '''
        if isnan(i):
            return None
        if (j <= 0) | ((i - j + 1) < 0) | (i > len(ds)):
            return None
        s = ds.iloc[(i - j + 1): i + 1]
        return s.loc[[s.idxmax()]]

    def idxmin(ds, i, j):
        '''
        返回pandas.Series指定位置、指定区间内的最小值及索引
        返回的是pandas.Series，只有一行，当有多个相同最小值时
        返回的是前面的那个
        注意：ds索引号为顺序号，l>0
        '''
        if isnan(i):
            return None
        if (j <= 0) | ((i - j + 1) < 0) | (i > len(ds)):
            return None
    #    print(f'i={i}')
        s = ds.iloc[(i - j + 1): i + 1]
        return s.loc[[s.idxmin()]]

    # Validate Arguments
    open = verify_series(open)
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
#    to_na = kwargs.pop('zerotona', True)  # 0置NaN
    in_threshold = kwargs.pop('in_threshold', 0.25)  # 涨幅阈值
    de_threshold = kwargs.pop('de_threshold', -0.15)  # 跌幅阈值

    # 上涨窗口和回调窗口长度
    m = int(m) if m and m > 0 else 55
    n = int(n) if n and n > 0 else 34
    m1 = int(m1) if m1 and m1 > 0 else 89

#    print(f'm1={m1},m={m},n={n}')
#    print(f'in_threshold={in_threshold},de_threshold={de_threshold}')
    ds = close  # 应该为pd.Series,索引为pd.DatetimeIndex
    indexname = ds.index.name  # 索引名
    name = ds.name  # 列名
    df1 = ds.reset_index()  # 变成了pd.DataFrame,索引为pd.RangeIndex，原索引变成列date
    ds2 = df1[name]  # 索引为pd.RangeIndex
    try:
        ds3 = pd.concat([idxmax(ds2, i, n) for i in range(len(ds2))])
        # 由于前面n-1行没有返回数据,索引ds3的长度要比ds2对n-1
    except:
        return None
    df3 = ds3.reset_index()  # 将原索引变成一列index
    df3.index += (n - 1)  # 由于前面n-1行没有返回数据，将所以往后移n-1

    df1['max'] = df3[name]  # 前n周期最大值
    df1['idxmax'] = df3['index']  # 最大值对应的索引序号

    ds4 = None
    idxmax1 = None  # 记录上一个序号
    for i in range(len(ds2)):
        idxmax = df1.iloc[i]['idxmax']
        if not isnan(idxmax):
            if idxmax != idxmax1:  # 与上个记录序号不同，则重新计算
                tmp = idxmin(ds2, int(idxmax), m)
                idxmax1 = idxmax   # 记录当前序号
        else:
            tmp = None
        if tmp is not None:
            ds4 = pd.concat([ds4, tmp])

    if ds4 is None:
        df1['min'] = npNaN
        df1['idxmin'] = npNaN
    else:
        df4 = ds4.reset_index()
        df4.index += (len(ds2)-len(ds4))  # 由于前面有较多行未返回数据
        df1['min'] = df4[name]
        df1['idxmin'] = df4['index']

    ds5 = None
    idxmax1 = None  # 记录上一个序号
    for i in range(len(ds2)):
        idxmax = df1.iloc[i]['idxmax']
        if not isnan(idxmax):
            if idxmax != idxmax1:  # 与上个记录序号不同，则重新计算
                tmp = idxmin(ds2, int(idxmax), m1)
                idxmax1 = idxmax   # 记录当前序号
        else:
            tmp = None
        if tmp is not None:
            ds5 = pd.concat([ds5, tmp])

    if ds5 is None:
        df1['min1'] = npNaN
        df1['idxmin1'] = npNaN
    else:
        df5 = ds5.reset_index()
        df5.index += (len(ds2)-len(ds5))  # 由于前面有较多行未返回数据
        df1['min1'] = df5[name]
        df1['idxmin1'] = df5['index']

    df1 = df1.assign(n_days=df1.index-df1['idxmax'])  # 当前位置距离高点天数
    df1 = df1.assign(m_days=df1.index-df1['idxmin'])  # 当前位置距离低点天数
    df1 = df1.assign(decreasing=df1['close']/df1['max']-1)
    df1 = df1.assign(increasing=df1['max']/df1['min']-1)
    df1 = df1.assign(increasing1=df1['max']/df1['min1']-1)

    df1 = df1.assign(double_bott=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)))
    df1 = df1.assign(double_bott1=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)
                     & (df1['increasing'] <= df1['increasing1']*1.05)))

    df1['double_bott'] = df1['double_bott'].astype(int)
    df1['double_bott'] = df1['double_bott'].replace(0, npNaN)
    df1['double_bott1'] = df1['double_bott1'].astype(int)
    df1['double_bott1'] = df1['double_bott1'].replace(0, npNaN)
#    ln = len(df1)
#    print(f'len(df1)={ln}')
    df = df1.set_index(indexname)
    df = df.drop(columns=name)  # 删除close列
    df = df.rename(columns={'max': f'max_{n}',
                            'min': f'min_{m}',
                            'min1': f'min_{m1}',
                            'decreasing': f'decreasing_{n}',
                            'increasing': f'increasing_{m}',
                            'increasing1': f'increasing_{m1}'})
#    if to_na:
#        df = df.replace(0, npNaN)
    return df


doublebottom.__doc__ = \
    '''
    双底形态研究：研究最长m+n窗口内上涨回调的情况。尽管取名是双底研究，不一定
    是双底，也可能是上涨趋势中的回调。
    m:近期高点前查找低点的窗口长度
    n:近期查找高点的窗口长度
    in_threshold:涨幅阈值，为正值
    de_threshold:回调跌幅阈值，为负值
    '''
