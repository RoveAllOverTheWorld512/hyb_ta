# -*- coding: utf-8 -*-
from ..overlap.hlc3 import hlc3
from ..overlap.sma import sma
from ..statistics.mad import mad
from ..utils import get_offset, verify_series

def cci(high, low, close, length=None, c=None, offset=None, **kwargs):
    """Indicator: Commodity Channel Index (CCI)"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = int(length) if length and length > 0 else 20
    c = float(c) if c and c > 0 else 0.015
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    typical_price = hlc3(high=high, low=low, close=close)
    mean_typical_price = sma(typical_price, length=length)
    mad_typical_price = mad(typical_price, length=length)

    cci = typical_price - mean_typical_price
    cci /= c * mad_typical_price

    # Offset
    if offset != 0:
        cci = cci.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        cci.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        cci.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    cci.name = f"CCI_{length}_{c}"
    cci.category = 'momentum'

    return cci



cci.__doc__ = \
"""Commodity Channel Index (CCI)

Commodity Channel Index is a momentum oscillator used to primarily identify
overbought and oversold levels relative to a mean.

Sources:
    https://www.tradingview.com/wiki/Commodity_Channel_Index_(CCI)

Calculation:
    Default Inputs:
        length=20, c=0.015
    SMA = Simple Moving Average
    MAD = Mean Absolute Deviation
    tp = typical_price = hlc3 = (high + low + close) / 3
    mean_tp = SMA(tp, length)
    mad_tp = MAD(tp, length)
    CCI = (tp - mean_tp) / (c * mad_tp)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 20
    c (float):  Scaling Constant.  Default: 0.015
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""