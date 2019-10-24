# -*- coding: utf-8 -*-
from numpy import log as nplog
from ..utils import get_offset, verify_series

def log_return(close, length=None, cumulative=False, offset=None, **kwargs):
    """Indicator: Log Return"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 1
    offset = get_offset(offset)

    # Calculate Result
    log_return = nplog(close).diff(periods=length)

    if cumulative:
        log_return = log_return.cumsum()

    # Offset
    if offset != 0:
        log_return = log_return.shift(offset)

    # Name & Category
    log_return.name = f"{'CUM' if cumulative else ''}LOGRET_{length}"
    log_return.category = 'performance'

    return log_return



log_return.__doc__ = \
"""Log Return

Calculates the logarithmic return of a Series.
See also: help(df.ta.log_return) for additional **kwargs a valid 'df'.

Sources:
    https://stackoverflow.com/questions/31287552/logarithmic-returns-in-pandas-dataframe

Calculation:
    Default Inputs:
        length=1, cumulative=False
    LOGRET = log( close.diff(periods=length) )
    CUMLOGRET = LOGRET.cumsum() if cumulative

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 20
    cumulative (bool): If True, returns the cumulative returns.  Default: False
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""