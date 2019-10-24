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


def doublebottom(open, high, low, close, m=None, n=None, **kwargs):
    '''
    双底形态研究：
    '''
    def idxmax(ds, i, l):
        '''
        返回pandas.Series指定位置、指定区间内的最大值及索引
        注意：ds索引号为顺序号，l>0
        '''
        if isnan(i):
            return None
        if (l <= 0) | ((i - l + 1) < 0) | (i > len(ds)):
            return None
        s = ds.iloc[(i - l + 1): i + 1]
        return s.loc[[s.idxmax()]]

    def idxmin(ds, i, l):
        '''
        返回pandas.Series指定位置、指定区间内的最小值及索引
        注意：ds索引号为顺序号，l>0
        '''
        if isnan(i):
            return None
        if (l <= 0) | ((i - l + 1) < 0) | (i > len(ds)):
            return None
    #    print(f'i={i}')
        s = ds.iloc[(i - l + 1): i + 1]
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

    ds = close  # 应该为pd.Series,索引为pd.DatetimeIndex
    indexname = ds.index.name
    name = ds.name
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

    try:
        ds4 = pd.concat([(idxmin(ds2, int(df1.iloc[i]['idxmax']), m)
                          if not isnan(df1.iloc[i]['idxmax']) else None)
                        for i in range(len(ds2))])
        # n周期内最高点前m周期内的最低点，这里的最高、最低只是知道窗口内的，
        # 可能在下降趋势或上升趋势的中部某个位置，不是趋势真正的转折位置
        # 注意isnan(), 这就是numpy.float64数据类型nan，不是None,np.NaN
    except:
        return None
    df4 = ds4.reset_index()
    df4.index += (len(ds2)-len(ds4))  # 由于前面有较多行未返回数据
    df1['min'] = df4[name]
    df1['idxmin'] = df4['index']

    df1 = df1.assign(n_days=df1.index-df1['idxmax'])  # 当前位置距离高点天数
    df1 = df1.assign(m_days=df1.index-df1['idxmin'])  # 当前位置距离低点天数
    df1 = df1.assign(decreasing=df1['close']/df1['max']-1)
    df1 = df1.assign(increasing=df1['max']/df1['min']-1)
    df1 = df1.assign(double_bott=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)))
    df1['double_bott'] = df1['double_bott'].astype(int)
    df1['double_bott'] = df1['double_bott'].replace(0, npNaN)

    df = df1.set_index(indexname)
    df = df.drop(columns=name)  # 删除close列
    df = df.rename(columns={'max': f'max_{n}',
                            'min': f'min_{m}',
                            'decreasing': f'decreasing_{n}',
                            'increasing': f'decreasing_{m}'})
#    if to_na:
#        df = df.replace(0, npNaN)
    return df


doublebottom.__doc__ = \
    '''
    双底形态研究：
    '''
