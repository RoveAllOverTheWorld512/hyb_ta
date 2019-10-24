# -*- coding: utf-8 -*-
from pandas import DataFrame
from ..overlap.rma import rma
from ..volatility.atr import atr
from ..utils import get_drift, get_offset, verify_series, zero

def adx(high, low, close, length=None, drift=None, offset=None, **kwargs):
    """Indicator: ADX"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = length if length and length > 0 else 14
    drift = get_drift(drift)
    offset = get_offset(offset)

    # Calculate Result
    _atr = atr(high=high, low=low, close=close, length=length)

    up = high - high.shift(drift)
    dn = low.shift(drift) - low

    pos = ((up > dn) & (up > 0)) * up
    neg = ((dn > up) & (dn > 0)) * dn

    pos = pos.apply(zero)
    neg = neg.apply(zero)

    dmp = (100 / _atr) * rma(close=pos, length=length)
    dmn = (100 / _atr) * rma(close=neg, length=length)

    dx = 100 * (dmp - dmn).abs() / (dmp + dmn)
    adx = rma(close=dx, length=length)

    # Offset
    if offset != 0:
        dmp = dmp.shift(offset)
        dmn = dmn.shift(offset)
        adx = adx.shift(offset)

    # Handle fills
    if 'fillna' in kwargs:
        adx.fillna(kwargs['fillna'], inplace=True)
        dmp.fillna(kwargs['fillna'], inplace=True)
        dmn.fillna(kwargs['fillna'], inplace=True)
    if 'fill_method' in kwargs:
        adx.fillna(method=kwargs['fill_method'], inplace=True)
        dmp.fillna(method=kwargs['fill_method'], inplace=True)
        dmn.fillna(method=kwargs['fill_method'], inplace=True)

    # Name and Categorize it
    adx.name = f"ADX_{length}"
    dmp.name = f"DMP_{length}"
    dmn.name = f"DMN_{length}"

    adx.category = dmp.category = dmn.category = 'trend'

    # Prepare DataFrame to return
    data = {adx.name: adx, dmp.name: dmp, dmn.name: dmn}
    adxdf = DataFrame(data)
    adxdf.name = f"ADX_{length}"
    adxdf.category = 'trend'

    return adxdf



adx.__doc__ = \
"""Average Directional Movement (ADX)

Average Directional Movement is meant to quantify trend strength by measuring
the amount of movement in a single direction.

Sources:
    https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/average-directional-movement-adx/

Calculation:
    DMI ADX TREND 2.0 by @TraderR0BERT, NETWORTHIE.COM
        //Created by @TraderR0BERT, NETWORTHIE.COM, last updated 01/26/2016
        //DMI Indicator
        //Resolution input option for higher/lower time frames
        study(title="DMI ADX TREND 2.0", shorttitle="ADX TREND 2.0")

        adxlen = input(14, title="ADX Smoothing")
        dilen = input(14, title="DI Length")
        thold = input(20, title="Threshold")

        threshold = thold

        //Script for Indicator
        dirmov(len) =>
            up = change(high)
            down = -change(low)
            truerange = rma(tr, len)
            plus = fixnan(100 * rma(up > down and up > 0 ? up : 0, len) / truerange)
            minus = fixnan(100 * rma(down > up and down > 0 ? down : 0, len) / truerange)
            [plus, minus]

        adx(dilen, adxlen) =>
            [plus, minus] = dirmov(dilen)
            sum = plus + minus
            adx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)
            [adx, plus, minus]

        [sig, up, down] = adx(dilen, adxlen)
        osob=input(40,title="Exhaustion Level for ADX, default = 40")
        col = sig >= sig[1] ? green : sig <= sig[1] ? red : gray

        //Plot Definitions Current Timeframe
        p1 = plot(sig, color=col, linewidth = 3, title="ADX")
        p2 = plot(sig, color=col, style=circles, linewidth=3, title="ADX")
        p3 = plot(up, color=blue, linewidth = 3, title="+DI")
        p4 = plot(up, color=blue, style=circles, linewidth=3, title="+DI")
        p5 = plot(down, color=fuchsia, linewidth = 3, title="-DI")
        p6 = plot(down, color=fuchsia, style=circles, linewidth=3, title="-DI")
        h1 = plot(threshold, color=black, linewidth =3, title="Threshold")

        trender = (sig >= up or sig >= down) ? 1 : 0
        bgcolor(trender>0?black:gray, transp=85)

        //Alert Function for ADX crossing Threshold
        Up_Cross = crossover(up, threshold)
        alertcondition(Up_Cross, title="DMI+ cross", message="DMI+ Crossing Threshold")
        Down_Cross = crossover(down, threshold)
        alertcondition(Down_Cross, title="DMI- cross", message="DMI- Crossing Threshold")

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int): It's period.  Default: 14
    drift (int): The difference period.   Default: 1
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: adx, dmp, dmn columns.
"""