# -*- coding: utf-8 -*-
"""
Created on 2019-10-05 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

trend reversal pattern趋势反转形态
top reversal pattern顶部反转形态

"""

from pandas import DataFrame
from numpy import NaN as npNaN
from ..utils import verify_series
from ..overlap.hl2 import hl2
from ..overlap.sma import sma


def topreversal(open, high, low, close, length=None, offset=None, **kwargs):

    # Validate Arguments
    open = verify_series(open)
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    to_na = kwargs.pop('zerotona', True)  # 0置NaN
    bias_threshold = kwargs.pop('bias_threshold', 20)  # bias阈值
    shadow_threshold = kwargs.pop('shadow_threshold', -0.05)  # 影线长度阈值

    # 移动窗口长度和偏移量
    length = int(length) if length and length > 0 else 13
    offset = int(offset) if offset and offset > 0 else 8

    # Calculate Result
    hl2_ = hl2(high, low)  # K线中点
    # K线中点简单移动平均线，
    line = sma(hl2_, length=length).shift(offset)

    # 收盘价相对均线乖离率
    bias = (close - line) / line * 100.00
    
    # 连续三天，高点逐次升高，当日为最高，当日收阴线，且收在下半部
    v1 = (high.diff(1) > 0)  #今日高点高于昨日
    v2 = (v1 & v1.shift(1))  #3日高点逐次升高
    v3 = (close < open)  # 收阴线
    hl = high - low  # K线长度
    ch = close - high  # 下杀动能
    v4 = (abs(ch) > (hl * 1 / 2))  # 收盘在K线下半部
    v5 = (ch / close.shift(1)) < shadow_threshold  # 下杀动能超过前收盘价的3%
    top0 = (v4 & v5)  # 收在下半部，下杀动能超过3%
    top1 = (top0 & v2 & v3)  # 3日高点逐次升高，收阴线，收在K线下半部，下杀动能超过3%
    top = top0
    top_reversal = (bias > bias_threshold) & top
    top = top.astype(int)
    top_reversal = top_reversal.astype(int)
    top_reversal_high = high * top_reversal
    
    bias.name = f'BIAS_A_{length}_{offset}'
    top.name = f'TOP'
    top_reversal.name = f'TOP_REVERSAL'
    top_reversal_high.name = f'TOP_REVERSAL_HIGH'
    # Prepare ractal DataFrame
    data = {bias.name: bias, top.name: top,
            top_reversal.name: top_reversal,
            top_reversal_high.name: top_reversal_high}
    reversaldf = DataFrame(data)
    if to_na:
        reversaldf = reversaldf.replace(0, npNaN)

    return reversaldf

    
    