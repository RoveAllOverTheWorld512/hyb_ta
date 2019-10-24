# -*- coding: utf-8 -*-
from numpy import sqrt as npsqrt
from .variance import variance
from ..utils import get_offset, verify_series

def stdev(close, length=None, offset=None, **kwargs):
    """Indicator: Standard Deviation"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 30
    offset = get_offset(offset)

    # Calculate Result
    stdev = variance(close=close, length=length).apply(npsqrt)

    # Offset
    if offset != 0:
        stdev = stdev.shift(offset)

    # Name & Category
    stdev.name = f"STDEV_{length}"
    stdev.category = 'statistics'

    return stdev



stdev.__doc__ = \
"""Rolling Standard Deviation

Sources:

Calculation:
    Default Inputs:
        length=30
    VAR = Variance
    STDEV = variance(close, length).apply(np.sqrt)

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 30
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""