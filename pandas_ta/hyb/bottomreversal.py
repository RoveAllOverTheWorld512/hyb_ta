# -*- coding: utf-8 -*-
"""
Created on 2019-10-05 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

trend reversal pattern趋势反转形态
bottom reversal pattern底部反转形态

"""

from pandas import DataFrame
from numpy import NaN as npNaN
from ..utils import verify_series
from ..overlap.hl2 import hl2
from ..overlap.sma import sma


def bottomreversal(open, high, low, close, length=None, offset=None, **kwargs):

    # Validate Arguments
    open = verify_series(open)
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    to_na = kwargs.pop('zerotona', True)  # 0置NaN
    bias_threshold = kwargs.pop('bias_threshold', -20)  # bias阈值
    shadow_threshold = kwargs.pop('shadow_threshold', 0.05)  # 影线长度阈值

    # 移动窗口长度和偏移量
    length = int(length) if length and length > 0 else 13
    offset = int(offset) if offset and offset > 0 else 8

    # Calculate Result
    hl2_ = hl2(high, low)  # K线中点
    # K线中点简单移动平均线，
    line = sma(hl2_, length=length).shift(offset)

    # 收盘价相对均线乖离率
    bias = (close - line) / line * 100.00
    
    # 连续三天，低点逐次降低，当日为最低，当日收阳线，且收在上部1/3
    v1 = (low.diff(1) < 0)  #今日低点低于昨日
    v2 = (v1 & v1.shift(1))  #3日低点逐次降低
    v3 = (close > open)  # 收阳线
    hl = high - low  # K线长度
    cl = close - low  # 上涨动能
    v4 = (cl > (hl * 1 / 2))  # 收盘在K线上部1/2
    v5 = (cl / close.shift(1)) > shadow_threshold  # 上涨动能超过前收盘价的3%
    bottom0 = (v4 & v5)  # 收在上半部，上涨动能超过3%
    bottom1 = (bottom0 & v2 & v3)  # 3日低点逐次降低，收阳线，收在上半部，上涨动能超过3%
    bottom = bottom0
    bottom_reversal = (bias < bias_threshold) & bottom
    bottom = bottom.astype(int)
    bottom_reversal = bottom_reversal.astype(int)
    bottom_reversal_low = low * bottom_reversal
    
    bias.name = f'BIAS_A_{length}_{offset}'
    bottom.name = f'BOTTOM'
    bottom_reversal.name = f'BOTTOM_REVERSAL'
    bottom_reversal_low.name = f'BOTTOM_REVERSAL_LOW'
    # Prepare ractal DataFrame
    data = {bias.name: bias, bottom.name: bottom,
            bottom_reversal.name: bottom_reversal,
            bottom_reversal_low.name: bottom_reversal_low}
    reversaldf = DataFrame(data)
    if to_na:
        reversaldf = reversaldf.replace(0, npNaN)
    
    return reversaldf

    
    