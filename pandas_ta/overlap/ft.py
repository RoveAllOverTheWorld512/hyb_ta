# -*- coding: utf-8 -*-
from ..utils import get_offset, pascals_triangle, verify_series, weights

def ft(close, length=None, offset=None, **kwargs):
    """Indicator: Fourier Transform (FT)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    offset = get_offset(offset)

    # Calculate Result
    ft = close

    # Offset
    if offset != 0:
        ft = ft.shift(offset)

    # Name & Category
    ft.name = f"FT_{length}"
    ft.category = 'overlap'

    return ft



ft.__doc__ = \
"""(Fast) Fourier Transform (FT)

The Fourier Transform implement

Source: Numpy, implemented by Kevin Johnson

Calculation:
    Default Inputs:
        length=100

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 10
    asc (bool): Recent values weigh more.  Default: True
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""