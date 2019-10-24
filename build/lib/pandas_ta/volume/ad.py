# -*- coding: utf-8 -*-
from ..utils import get_offset, verify_series

def ad(high, low, close, volume, open_=None, offset=None, **kwargs):
    """Indicator: Accumulation/Distribution (AD)"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    volume = verify_series(volume)
    offset = get_offset(offset)

    # Calculate Result
    if open_ is not None:
        open_ = verify_series(open_)
        ad = close - open_  # AD with Open
    else:                
        ad = 2 * close - high - low  # AD with High, Low, Close

    hl_range = high - low
    ad *= volume / hl_range
    ad = ad.cumsum()

    # Offset
    if offset != 0:
        ad = ad.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        ad.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        ad.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    ad.name = f"AD"
    ad.category = 'volume'

    return ad



ad.__doc__ = \
"""Accumulation/Distribution (AD)

Accumulation/Distribution indicator utilizes the relative position
of the close to it's High-Low range with volume.  Then it is cumulated.

Sources:
    https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/accumulationdistribution-ad/

Calculation:
    CUM = Cumulative Sum
    if 'open':
        AD = close - open
    else:
        AD = 2 * close - high - low

    hl_range = high - low
    AD = AD * volume / hl_range
    AD = CUM(AD)

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    volume (pd.Series): Series of 'volume's
    open (pd.Series): Series of 'open's
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""