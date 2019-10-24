# -*- coding: utf-8 -*-
from numpy import argmax as npargmax
from numpy import argmin as npargmin
from pandas import DataFrame
from ..utils import get_offset, verify_series

def aroon(close, length=None, offset=None, **kwargs):
    """Indicator: Aroon Oscillator"""
    # Validate Arguments
    close = verify_series(close)
    length = length if length and length > 0 else 14
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    def maxidx(x):
        return 100 * (int(npargmax(x)) + 1) / length

    def minidx(x):
        return 100 * (int(npargmin(x)) + 1) / length

    _close = close.rolling(length, min_periods=min_periods)
    aroon_up = _close.apply(maxidx, raw=True)
    aroon_down = _close.apply(minidx, raw=True)

    # Handle fills
    if 'fillna' in kwargs:
        aroon_up.fillna(kwargs['fillna'], inplace=True)
        aroon_down.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        aroon_up.fillna(method=kwargs['fill_method'], inplace=True)
        aroon_down.fillna(method=kwargs['fill_method'], inplace=True)

    # Offset
    if offset != 0:
        aroon_up = aroon_up.shift(offset)
        aroon_down = aroon_down.shift(offset)

    # Name and Categorize it
    aroon_up.name = f"AROONU_{length}"
    aroon_down.name = f"AROOND_{length}"

    aroon_down.category = aroon_up.category = 'trend'

    # Prepare DataFrame to return
    data = {aroon_down.name: aroon_down, aroon_up.name: aroon_up}
    aroondf = DataFrame(data)
    aroondf.name = f"AROON_{length}"
    aroondf.category = 'trend'

    return aroondf



aroon.__doc__ = \
"""Aroon (AROON)

Aroon attempts to identify if a security is trending and how strong.

Sources:
    https://www.tradingview.com/wiki/Aroon
    https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/aroon-ar/

Calculation:
    Default Inputs:
        length=1
    def maxidx(x):
        return 100 * (int(np.argmax(x)) + 1) / length

    def minidx(x):
        return 100 * (int(np.argmin(x)) + 1) / length

    _close = close.rolling(length, min_periods=min_periods)
    aroon_up = _close.apply(maxidx, raw=True)
    aroon_down = _close.apply(minidx, raw=True)

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 1
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: aroon_up, aroon_down columns.
"""
