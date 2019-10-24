# -*- coding: utf-8 -*-
"""
Created on 2019-10-21 13:33:16

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""
import pandas as pd
import numpy as np
from math import isnan


def idxmax(ds,i,l):
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

if isinstance(ds, pd.Series):
    name = ds.name    
if not isinstance(ds.index, pd.RangeIndex):
    ds1 = ds.reset_index()
    ds2 = ds1[name]

n = 34
ds3 = pd.concat([idxmax(ds2, i, n) for i in range(len(ds2))])
ds3 = ds3.reset_index()
ds3.index += (n - 1)  # 由于前面返回

ds1['max'] = ds3['close']
ds1['idxmax'] = ds3['index']

m = 34
ds4 = pd.concat([(idxmin(ds2, int(ds1.iloc[i]['idxmax']), m)
                  if not isnan(ds1.iloc[i]['idxmax']) else None)
                for i in range(len(ds2))])

ds4 = ds4.reset_index()
ds4.index += (len(ds2)-len(ds4))  # 由于前面返回
ds1['min'] = ds4['close']
ds1['idxmin'] = ds4['index']

ds1 = ds1.assign(decreasing=ds1['close']/ds1['max']-1)
ds1 = ds1.assign(increasing=ds1['max']/ds1['min']-1)
in_threshold = 0.25
de_threshold = -0.15
ds1 = ds1.assign(double_bott=((ds1['decreasing'] < de_threshold)
                 & (ds1['increasing'] > in_threshold)))
ds1['double_bott'] = ds1['double_bott'].astype(int)
ds1['double_bott'] = ds1['double_bott'].replace(0, np.NaN)

ds1.to_csv('tmp.csv')

