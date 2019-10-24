# -*- coding: utf-8 -*-
"""
Created on 2019-09-26 18:15:24

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from pandas import DataFrame
from numpy import NaN as npNaN
from ..utils import get_offset, verify_series


def up_or_down(series, fractal_type=1):

    hl_df = series.to_frame()

    if fractal_type == 1:
        # 与前一天比较，高于前一天为1
        hl_1 = (series.diff(1) > 0).astype(int)
        # 与前第二天比较，高于前第二天为1
        hl_2 = (series.diff(2) > 0).astype(int)
        # 与后一天比较，高于后一天为1
        hl1 = (series.diff(-1) > 0).astype(int)
        # 与后第二天比较，高于后第二天为1
        hl2 = (series.diff(-2) > 0).astype(int)
    else:
        # 与前一天比较，低于前一天为1
        hl_1 = (series.diff(1) < 0).astype(int)
        # 与前第二天比较，低于前第二天为1
        hl_2 = (series.diff(2) < 0).astype(int)
        # 与后一天比较，低于后一天为1
        hl1 = (series.diff(-1) < 0).astype(int)
        # 与后第二天比较，低于后第二天为1
        hl2 = (series.diff(-2) < 0).astype(int)

    # 同时高(低)于前两天为1
    hl_12 = ((hl_1 + hl_2) == 2).astype(int)
    # 同时高(低)于后两天为1
    hl12 = ((hl1 + hl2) == 2).astype(int)

    # 合并数据
    hl_df['hl_12'] = hl_12
    hl_df['hl12'] = hl12

    # 连续上涨（下跌）的只记录最后一个高(低)点
    i = 0
    while i < len(hl_df) - 1:
        if (hl_df.iloc[i + 1, 1] == 1):
            hl_df.iloc[i, 1] = 0
        i += 1

    # 间隔一天继续上涨（下跌）的去掉间隔前一天高（低）点
    i = 0
    while i < len(hl_df) - 2:
        if (hl_df.iloc[i + 2, 1] == 1):
            hl_df.iloc[i, 1] = 0
        i += 1

    # 逆序
    hl_df = hl_df.sort_index(ascending=False)

    # 连续下跌（上涨）只记录开始一天
    i = 0
    while i < len(hl_df) - 1:
        if (hl_df.iloc[i + 1, 2] == 1):
            hl_df.iloc[i, 2] = 0
        i += 1

    # 间隔一天继续下跌（上涨）的去掉间隔前一天高（低）点
    i = 0
    while i < len(hl_df) - 2:
        if (hl_df.iloc[i + 2, 2] == 1):
            hl_df.iloc[i, 2] = 0
        i += 1

    # 正序
    hl_df = hl_df.sort_index()

    # 去掉中继高（低）点
    i = 0
    bg = False
    ii = 0
    while i < len(hl_df):
        if (hl_df.iloc[i, 1] == 1):
            if bg:
                hl_df.iloc[ii, 1] = 0
            if (hl_df.iloc[i, 2] == 1):
                bg = False
            else:
                bg = True
                ii = i
        else:
            if (hl_df.iloc[i, 2] == 1):
                bg = False
            else:
                pass
        i += 1

    # 返回结果
    return hl_df['hl_12']


def fractals(high, low, offset=None, **kwargs):
    """
    Indicator: fractal
    """
    high = verify_series(high)
    low = verify_series(low)
    offset = get_offset(offset)
    to_na = kwargs.pop('zerotona', True)

    # Calculate Result
    fractal_up = up_or_down(high)
    fractal_down = up_or_down(low, 2)
    fractal_upvalue = fractal_up * high
    fractal_downvalue = fractal_down * low

    # Name it
    fractal_up.name = 'FRACTAL_UP'
    fractal_upvalue.name = 'FRACTAL_UPPRICE'
    fractal_down.name = 'FRACTAL_DOWN'
    fractal_downvalue.name = 'FRACTAL_DOWNPRICE'

    # Prepare ractal DataFrame
    data = {fractal_up.name: fractal_up, fractal_upvalue.name: fractal_upvalue,
            fractal_down.name: fractal_down, fractal_downvalue.name: fractal_downvalue}
    fractaldf = DataFrame(data)

    if to_na:
        fractaldf = fractaldf.replace(0, npNaN)

    fractaldf.category = 'hyb_ta'

    return fractaldf


fractals.__doc__ = \
    """
    分形（Fractal）是由比尔-威廉姆发明的，是结合不规则分形几何学和非线性动力学
的时间框架线，有蓝、红、绿三条。蓝线，是鳄鱼的颚。红线，是鳄鱼的牙齿。绿线，是鳄鱼的上
唇。基本上，无论实时价格往任何方向移动，鳄鱼线扮演着使我们的交易保持正当方向的罗盘角色。

Sources:
    https://www.investopedia.com/terms/f/fractal.asp
    https://www.ifcmarkets.com/en/ntx-indicators/alligator

Calculation:

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's

Kwargs:
    zerotona (bool, optional): Default: True.  If True, zero replace with Na

Returns:
    pd.DataFrame: a DataFrames.

"""
