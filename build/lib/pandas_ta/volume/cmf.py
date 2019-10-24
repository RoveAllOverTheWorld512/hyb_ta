# -*- coding: utf-8 -*-
from ..utils import get_offset, verify_series

def cmf(high, low, close, volume, open_=None, length=None, offset=None, **kwargs):
    """Indicator: Chaikin Money Flow (CMF)"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    volume = verify_series(volume)
    length = int(length) if length and length > 0 else 20
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)

    # Calculate Result
    if open_ is not None:
        open_ = verify_series(open_)
        ad = close - open_  # AD with Open
    else:                
        ad = 2 * close - high - low  # AD with High, Low, Close

    hl_range = high - low
    ad *= volume / hl_range
    cmf = ad.rolling(length, min_periods=min_periods).sum() / volume.rolling(length, min_periods=min_periods).sum()

    # Offset
    if offset != 0:
        cmf = cmf.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        cmf.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        cmf.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    cmf.name = f"CMF_{length}"
    cmf.category = 'volume'

    return cmf



cmf.__doc__ = \
"""Chaikin Money Flow (CMF)

Chailin Money Flow measures the amount of money flow volume over a specific
period in conjunction with Accumulation/Distribution.

Sources:
    https://www.tradingview.com/wiki/Chaikin_Money_Flow_(CMF)
    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:chaikin_money_flow_cmf

Calculation:
    Default Inputs:
        length=20
    if 'open':
        ad = close - open
    else:
        ad = 2 * close - high - low
    
    hl_range = high - low
    ad = ad * volume / hl_range
    CMF = SUM(ad, length) / SUM(volume, length)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    open (pd.Series): Series of 'open's
    volume (pd.Series): Series of 'volume's
    length (int): The short period.  Default: 20
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""