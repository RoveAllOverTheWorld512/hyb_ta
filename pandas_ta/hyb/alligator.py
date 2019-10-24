# -*- coding: utf-8 -*-
"""
Created on 2019-09-28 18:17:48

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""
from pandas import date_range, DataFrame, RangeIndex, Timedelta
from ..utils import get_offset, verify_series
from ..overlap.hl2 import hl2
from ..overlap.sma import sma

def alligator(high, low, long=None, mid=None, short=None, long_offset=None, \
              mid_offset=None, short_offset=None, **kwargs):

    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    
    long = int(long) if long and long > 0 else 13
    mid = int(mid) if mid and mid > 0 else 8
    short = int(short) if short and short > 0 else 5
    l = [long,mid,short]
    l.sort()
    short = l[0]
    mid = l[1]
    long = l[2]
    
    long_offset = int(long_offset) if long_offset and long_offset > 0 else 8
    mid_offset = int(mid_offset) if mid_offset and mid_offset > 0 else 5
    short_offset = int(short_offset) if short_offset and short_offset > 0 else 3
    l = [long_offset,mid_offset,short_offset]
    l.sort()
    short_offset = l[0]
    mid_offset = l[1]
    long_offset = l[2]

    # Calculate Result
    hl2_ = hl2(high, low)
    alligator_jaw = sma(hl2_, length=long).shift(long_offset)
    alligator_teeth = sma(hl2_, length=mid).shift(mid_offset)
    alligator_lips = sma(hl2_, length=short).shift(short_offset)

    # Handle fills
    if 'fillna' in kwargs:
        alligator_jaw.fillna(kwargs['fillna'], inplace=True)
        alligator_teeth.fillna(kwargs['fillna'], inplace=True)
        alligator_lips.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        alligator_jaw.fillna(method=kwargs['fill_method'], inplace=True)
        alligator_teeth.fillna(method=kwargs['fill_method'], inplace=True)
        alligator_lips.fillna(method=kwargs['fill_method'], inplace=True)

    # Name it
    alligator_jaw.name = f'ALLIGATOR_JAW_{long}_{long_offset}'
    alligator_teeth.name = f'ALLIGATOR_TEETH_{mid}_{mid_offset}'
    alligator_lips.name = f'ALLIGATOR_LIPS_{short}_{short_offset}'

    # Prepare ractal DataFrame
    data = {alligator_jaw.name: alligator_jaw,
            alligator_teeth.name: alligator_teeth,
            alligator_lips.name: alligator_lips}
    alligatordf = DataFrame(data)

    # Categorize it
    alligatordf.category = 'hyb_ta'

    return alligatordf


alligator.__doc__ = \
'''
    鳄鱼指标（Alligator）是由比尔-威廉姆发明的，是结合不规则分形几何学和非线性动力学
的时间框架线，有蓝、红、绿三条。蓝线，是鳄鱼的颚。红线，是鳄鱼的牙齿。绿线，是鳄鱼的上
唇。基本上，无论实时价格往任何方向移动，鳄鱼线扮演着使我们的交易保持正当方向的罗盘角色。

Sources:
    https://baike.baidu.com/item/鳄鱼指标/2328995
    https://www.ifcmarkets.com/en/ntx-indicators/alligator

Calculation:
    MEDIAN PRICE = (HIGH + LOW) / 2
    鳄鱼的下巴 = SMMA (MEDEAN PRICE, 13, 8)
    鳄鱼的牙齿 = SMMA (MEDEAN PRICE, 8, 5)
    鳄鱼的嘴唇 = SMMA (MEDEAN PRICE, 5, 3)
    注解:MEDIAN PRICE — 中间价；
    HIGH —最高价格柱；
    LOW — 最低价格柱；
    SMMA (A, B, C) — 顺畅移动平均线；
    ALLIGATORS JAW — 鳄鱼的下巴（蓝线）；
    ALLIGATORS TEETH — 鳄鱼的牙齿（红线） ；
    ALLIGATORS LIPS — 鳄鱼的嘴唇（绿线）。
    
Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    long (int): long period.  Default: 13
    mid (int): mid period.  Default: 8
    short (int): short period.  Default: 5
    long_offset (int): How many periods to offset the result.  Default: 8
    mid_offset (int): How many periods to offset the result.  Default: 5
    short_offset (int): How many periods to offset the result.  Default: 3

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: a DataFrames.


'''


    