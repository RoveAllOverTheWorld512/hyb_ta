# -*- coding: utf-8 -*-
from math import pi
from math import sin
from pandas import Series
from ..utils import get_offset, pascals_triangle, verify_series, weights

def sinwma(close, length=None, asc=None, offset=None, **kwargs):
    """Indicator: Sine Weighted Moving Average (SINWMA) by Everget of TradingView"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 14
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    sines = Series([sin((i + 1) * pi / (length + 1)) for i in range(0, length)])
    w = sines / sines.sum()

    sinwma = close.rolling(length, min_periods=length).apply(weights(w), raw=True)

    # Offset
    if offset != 0:
        sinwma = sinwma.shift(offset)

    # Name & Category
    sinwma.name = f"SINWMA_{length}"
    sinwma.category = 'overlap'

    return sinwma



sinwma.__doc__ = \
"""Sine Weighted Moving Average (SWMA)

A weighted average using sine cycles.  The middle term(s) of the average have the highest
weight(s).

Source:
    https://www.tradingview.com/script/6MWFvnPO-Sine-Weighted-Moving-Average/
    Author: Everget (https://www.tradingview.com/u/everget/)

Calculation:
    Default Inputs:
        length=10

    def weights(w):
        def _compute(x):
            return np.dot(w * x)
        return _compute

    sines = Series([sin((i + 1) * pi / (length + 1)) for i in range(0, length)])
    w = sines / sines.sum()
    SINWMA = close.rolling(length, min_periods=length).apply(weights(w), raw=True)

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 10
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""