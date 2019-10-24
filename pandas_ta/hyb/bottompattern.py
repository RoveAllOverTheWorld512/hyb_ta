# -*- coding: utf-8 -*-
"""
Created on 2019-10-05 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

bottom pattern底部形态研究

"""

from pandas import DataFrame
from numpy import NaN as npNaN
from ..utils import verify_series
from ..overlap.hl2 import hl2
from ..overlap.sma import sma


def bottompattern(open, high, low, close, length=None, offset=None, **kwargs):

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
#    v1 = (low.diff(1) < 0)  #今日低点低于昨日
#    v2 = (v1 & v1.shift(1))  #3日低点逐次降低
#    close_above = (close > low)  # 收阳线
    hl = high - low  # K线长度
    cl = close - low  # 上涨动能
    close_upper_half = (cl > (hl * 1 / 2))  # 收盘在K线上部1/2
    close_upper_half = close_upper_half.astype(int)
    rising_momentum = cl / close.shift(1)  # 上涨动量
    v4 = bias < bias_threshold  # 乖离率超出阈值
    v5 = rising_momentum > shadow_threshold  # 上涨动能超过前收盘价的3%
    bottom_reversal = v4 & v5
    bottom_reversal = bottom_reversal.astype(int)

    hhv = high.rolling(13).max()
    
    

    bias.name = f'BIAS_A_{length}_{offset}'
    rising_momentum.name = f'RISING_MOMENTUM'
    close_upper_half.name = f'CLOSE_UPPER_HALF'
    bottom_reversal.name = f'BOTTOM_REVERSAL'
    # Prepare ractal DataFrame
    data = {bias.name: bias,
            rising_momentum.name: rising_momentum,
            close_upper_half.name: close_upper_half,
            bottom_reversal.name: bottom_reversal}
    reversaldf = DataFrame(data)
    if to_na:
        reversaldf = reversaldf.replace(0, npNaN)
    return reversaldf


bottompattern.__doc__ = \
    '''
    底部形态研究：
    bias:收盘价与鳄鱼线蓝线的乖离率
    rising_momentum:上涨动量，收盘价与最低价之差与前收盘价比值
    close_upper_half:收盘在K线的上半部分
    bottom_reversal:底部反转，乖离率大于设定阈值，也就是远离鳄鱼嘴，
                    上涨动量大于设定阈值，也就是有足够的上涨意愿
    '''
