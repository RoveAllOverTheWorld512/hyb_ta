# -*- coding: utf-8 -*-
from .ema import ema
from .hma import hma
from .sma import sma
from .wma import wma
from ..utils import get_offset, verify_series

def zlma(close, length=None, offset=None, mamode=None, **kwargs):
    """Indicator: Zero Lag Moving Average (ZLMA)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    min_periods = int(kwargs['min_periods']) if 'min_periods' in kwargs and kwargs['min_periods'] is not None else length
    offset = get_offset(offset)
    mamode = mamode.lower() if mamode else None

    # Calculate Result
    lag = int(0.5 * (length - 1))
    close = 2 * close - close.shift(lag)
    if mamode is None or mamode == 'ema':
        zlma = ema(close, length=length, **kwargs)
        kind = "E"
    if mamode == 'hma':
        zlma = hma(close, length=length, **kwargs)
        kind = "H"
    if mamode == 'sma':
        zlma = sma(close, length=length, **kwargs)
        kind = "S"
    if mamode == 'wma':
        zlma = wma(close, length=length, **kwargs)
        kind = "W"

    # Offset
    if offset != 0:
        zlma = zlma.shift(offset)

    # Name & Category
    zlma.name = f"ZL{kind}MA_{length}"
    zlma.category = 'overlap'

    return zlma



zlma.__doc__ = \
"""Zero Lag Moving Average (ZLMA)

The Zero Lag Moving Average attempts to eliminate the lag associated
with moving averages.  This is an adaption created by John Ehler and Ric Way.

Sources:
    https://en.wikipedia.org/wiki/Zero_lag_exponential_moving_average

Calculation:
    Default Inputs:
        length=10, mamode=EMA
    EMA = Exponential Moving Average
    lag = int(0.5 * (length - 1))
    source = 2 * close - close.shift(lag)
    ZLMA = EMA(source, length)

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 10
    mamode (str): Two options: None or 'ema'.  Default: 'ema'
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""