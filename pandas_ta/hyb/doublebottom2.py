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


def doublebottom(open, high, low, close, m1=None, m=None, n1=None, n=None, **kwargs):
    '''
    双底形态研究：研究最长m+n窗口内上涨回调的情况。尽管取名是双底研究，不一定
    是双底，也可能是上涨趋势中的回调。
    m1:近期高点前查找低点的窗口长度  m1>m
    m:近期高点前查找低点的窗口长度
    n1:近期查找高点的窗口长度  n1>n
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
    n1 = int(n1) if n1 and n1 > 0 else 55

#    print(f'm1={m1},m={m},n={n}')
#    print(f'in_threshold={in_threshold},de_threshold={de_threshold}')
    ds = close  # 应该为pd.Series,索引为pd.DatetimeIndex
    indexname = ds.index.name  # 索引名
    name = ds.name  # 列名
    df1 = ds.reset_index()  # 变成了pd.DataFrame,索引为pd.RangeIndex，原索引变成列date
    ds2 = df1[name]  # 索引为pd.RangeIndex
    # n天内高点
    try:
        ds3 = pd.concat([idxmax(ds2, i, n) for i in range(len(ds2))])
        # 由于前面n-1行没有返回数据,索引ds3的长度要比ds2对n-1
    except:
        return None
    df3 = ds3.reset_index()  # 将原索引变成一列index
    dt = df1[indexname].iloc[df3['index']].to_frame()  # 注意其索引
    dt = dt.reset_index(drop=True)
    df3['idxmaxdate'] = dt['date']
    df3.index += (n - 1)  # 由于前面n-1行没有返回数据，将所以往后移n-1
    df1['max'] = df3[name]  # 前n周期最大值
    df1['idxmax'] = df3['index']  # 最大值对应的索引序号
    df1['idxmaxdate'] = df3['idxmaxdate']

    try:
        ds6 = pd.concat([idxmax(ds2, i, n1) for i in range(len(ds2))])
        # 由于前面n1-1行没有返回数据,索引ds3的长度要比ds2对n-1
    except:
        return None
    df6 = ds6.reset_index()  # 将原索引变成一列index
    dt = df1[indexname].iloc[df6['index']].to_frame()  # 注意其索引
    dt = dt.reset_index(drop=True)
    df6['idxmaxdate1'] = dt['date']
    df6.index += (n1 - 1)  # 由于前面n-1行没有返回数据，将所以往后移n-1
    df1['max1'] = df6[name]  # 前n周期最大值
    df1['idxmax1'] = df6['index']  # 最大值对应的索引序号
    df1['idxmaxdate1'] = df6['idxmaxdate1']

    ds4 = None
    idx1 = None  # 记录上一个序号
    for i in range(len(ds2)):
        idx = df1.iloc[i]['idxmax']
        if not isnan(idx):
            if idx != idx1:  # 与上个记录序号不同，则重新计算
                tmp = idxmin(ds2, int(idx), m)
                idx1 = idx   # 记录当前序号
        else:
            tmp = None
        if tmp is not None:
            ds4 = pd.concat([ds4, tmp])

    if ds4 is None:
        df1['min'] = npNaN
        df1['idxmin'] = npNaN
        df1['idxmindate'] = npNaN
    else:
        df4 = ds4.reset_index()
        dt = df1[indexname].iloc[df4['index']].to_frame()  # 注意其索引
        dt = dt.reset_index(drop=True)
        df4['idxmindate'] = dt['date']
        df4.index += (len(ds2)-len(ds4))  # 由于前面有较多行未返回数据
        df1['min'] = df4[name]
        df1['idxmin'] = df4['index']
        df1['idxmindate'] = df4['idxmindate']

    ds5 = None
    idx1 = None  # 记录上一个序号
    for i in range(len(ds2)):
        idx = df1.iloc[i]['idxmax']
        if not isnan(idx):
            if idx != idx1:  # 与上个记录序号不同，则重新计算
                tmp = idxmin(ds2, int(idx), m1)
                idx1 = idx   # 记录当前序号
        else:
            tmp = None
        if tmp is not None:
            ds5 = pd.concat([ds5, tmp])

    if ds5 is None:
        df1['min1'] = npNaN
        df1['idxmin1'] = npNaN
        df1['idxmindate1'] = npNaN
    else:
        df5 = ds5.reset_index()
        dt = df1[indexname].iloc[df5['index']].to_frame()  # 注意其索引
        dt = dt.reset_index(drop=True)
        df5['idxmindate1'] = dt['date']
        df5.index += (len(ds2)-len(ds5))  # 由于前面有较多行未返回数据
        df1['min1'] = df5[name]
        df1['idxmin1'] = df5['index']
        df1['idxmindate1'] = df5['idxmindate1']
        
    # 两个低点间的高点
    ds7 = None
    idx = None  # 记录上一个序号
    idx1 = None  # 记录上一个序号
    for i in range(len(ds2)):
        idxm = df1.iloc[i]['idxmin']
        idxm1 = df1.iloc[i]['idxmin1']
        if not isnan(idxm) and not isnan(idxm1):
            if idxm != idx or idxm1 != idx1:
                if idxm != idxm1:
                    tmp = idxmax(ds2, int(idxm), int(idxm - idxm1))
                else:
                    tmp = pd.Series(ds2.iloc[int(idxm)], index = [idxm], name=name)                    
                idx = idxm
                idx1 = idxm1
        else:
            tmp = None
        if tmp is not None:
            ds7 = pd.concat([ds7, tmp])

    if ds7 is None:
        df1['max2'] = npNaN
        df1['idxmax2'] = npNaN
        df1['idxmaxdate2'] = npNaN
    else:
        df7 = ds7.reset_index()
        dt = df1[indexname].iloc[df7['index']].to_frame()  # 注意其索引
        dt = dt.reset_index(drop=True)
        df7['idxmaxdate2'] = dt['date']
        df7.index += (len(ds2)-len(ds7))  # 由于前面有较多行未返回数据
        df1['max2'] = df7[name]
        df1['idxmax2'] = df7['index']
        df1['idxmaxdate2'] = df7['idxmaxdate2']
    
    df1 = df1.assign(n_days=df1.index-df1['idxmax'])  # 当前位置距离高点天数
    df1 = df1.assign(n1_days=df1.index-df1['idxmax1'])  # 当前位置距离远高点天数
    df1 = df1.assign(m_days=df1.index-df1['idxmin'])  # 当前位置距离低点天数
    df1 = df1.assign(m1_days=df1.index-df1['idxmin1'])  # 当前位置距离远低点天数
    df1 = df1.assign(min_days=df1['idxmin']-df1['idxmin1'])  # 两个低点间交易日天数
    df1 = df1.assign(decreasing=df1['close']/df1['max']-1)  # 近高点回调幅度
    df1 = df1.assign(decreasing1=df1['close']/df1['max1']-1)  # 远高点回调幅度
    df1 = df1.assign(increasing=df1['max']/df1['min']-1)  # 近低点到高点的上涨幅度
    df1 = df1.assign(increasing1=df1['max']/df1['min1']-1)  # 远低点到高点的上涨幅度
    df1 = df1.assign(min_increasing=df1['min']/df1['min1']-1)  # 低点间的上涨幅度
    df1 = df1.assign(min_increasing1=df1['min_increasing']/df1['min_days'])
    df1.loc[(df1['min_days'] == 0), "min_increasing1"] = 0
    # 低点间日平均上涨幅度
    # 两个低点间每个交易日涨幅

    df1 = df1.assign(double_bott=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)))
    df1 = df1.assign(double_bott1=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)
                     & (df1['max'] == df1['max1'])
                     & (df1['max2'] < df1['max'])
                     & (df1['min'] / df1['min1'] < 1.05)))  # 两个低点相差小于5%
    # 双底确定条件：通过寻找远近两个高点，如果两个高点重合，说明这个高点为近期高点
    # 不是下降通道的中继高点
    # 从这个高点往前寻找远近两个低点，两个低点相差不大，可以用每日
    df1 = df1.assign(double_bott2=((df1['decreasing'] < de_threshold)
                     & (df1['increasing'] > in_threshold)
                     & (df1['max'] == df1['max1'])
                     & (df1['max2'] < df1['max'])
                     & (df1['min_increasing1'] < 0.003)))  # 两个低点日均涨幅小于3‰
    # 双底确定条件：通过寻找远近两个高点，如果两个高点重合，说明这个高点为近期高点
    # 不是下降通道的中继高点
    # 从这个高点往前寻找远近两个低点，两个低点相差不大，可以用每日

    df1['double_bott'] = df1['double_bott'].astype(int)
    df1['double_bott'] = df1['double_bott'].replace(0, npNaN)
    df1['double_bott1'] = df1['double_bott1'].astype(int)
    df1['double_bott1'] = df1['double_bott1'].replace(0, npNaN)
    df1['double_bott2'] = df1['double_bott2'].astype(int)
    df1['double_bott2'] = df1['double_bott2'].replace(0, npNaN)
#    ln = len(df1)
#    print(f'len(df1)={ln}')
    df = df1.set_index(indexname)
    df = df.drop(columns=[name, 'idxmax', 'idxmax1', 'idxmax2', 'idxmin', 'idxmin1'])  # 删除close列
    df = df.rename(columns={'max': f'max_{n}',
                            'max1': f'max_{n1}',
                            'min': f'min_{m}',
                            'min1': f'min_{m1}',
                            'decreasing': f'decreasing_{n}',
                            'decreasing1': f'decreasing_{n1}',
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
    思路：假定股价经过较长时间的盘整，近期拉升，最近回调。通过查找n天内和n1天内的高点
    如果两个高点重合，即确定该高点为近期高点（位置idxmax）。再从idxmax往前查找m天内和
    m1天内点近远两个低点（idxmin,idxmin1），
    '''
