# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandas.core.base import PandasObject 
from .utils import *

@pd.api.extensions.register_dataframe_accessor('ta')
class AnalysisIndicators(PandasObject):
    """AnalysisIndicators is class that extends the Pandas DataFrame via
    Pandas @pd.api.extensions.register_dataframe_accessor('name') decorator.

    This Pandas Extension is named 'ta' for Technical Analysis that allows us
    to apply technical indicators with an one extension.  Even though 'ta' is
    now a Pandas DataFrame Extension, you can still call the Indicators
    individually. However many of the Indicators have been updated and new ones
    added, so make sure to check help.
    
    By default the 'ta' extensions uses lower case column names: open, high,
    low, close, and volume.  You can override the defaults but providing the
    it's replacement name when calling the indicator.  For example, to call the
    indicator hl2().  

    With 'default' columns: open, high, low, close, and volume.
    >>> df.ta.hl2()
    >>> df.ta(kind='hl2')

    With DataFrame columns: Open, High, Low, Close, and Volume.
    >>> df.ta.hl2(high='High', low='Low')
    >>> df.ta(kind='hl2', high='High', low='Low')

    Args:
        kind (str, optional): Default: None.  Name of the indicator.  Converts
            kind to lowercase before calling.
        timed (bool, optional): Default: False.  Curious about the execution
            speed?  Well it's not ground breaking, but you can enable with True.
        kwargs: Extension specific modifiers.
            append (bool, optional):  Default: False.  When True, it appends to
            result column(s) of the indicator onto the DataFrame.

    Returns:
        Most Indicators will return a Pandas Series.  Others like MACD, BBANDS,
        KC, et al will return a Pandas DataFrame.  Ichimoku on the other hand
        will return two DataFrames, the Ichimoku DataFrame for the known period
        and a Span DataFrame for the future of the Span values.

    Let's get started!

    1. Loading the 'ta' module:
    >>> import pandas as pd
    >>> import pandas_ta as ta

    2. Load some data:
    >>> df = pd.read_csv('AAPL.csv', index_col='date', parse_dates=True)
    
    3. Help!
    3a. General Help:
    >>> help(df.ta)
    >>> df.ta()
    3a. Indicator Help:
    >>> help(ta.apo)
    3b. Indicator Extension Help:
    >>> help(df.ta.apo)

    4. Ways of calling an indicator.
    4a. Calling just the MACD indicator without 'ta' DataFrame extension.
    >>> ta.apo(df['close'])
    4b. Calling just the MACD indicator with 'ta' DataFrame extension.
    >>> df.ta.apo()
    4c. Calling using kind.
    >>> df.ta(kind='apo')

    5. Working with kwargs
    5a. Append the result to the working df.
    >>> df.ta.apo(append=True)
    5b. Timing an indicator.
    >>> apo = df.ta(kind='apo', timed=True)
    >>> print(apo.timed)
    """

    def __init__(self, df, **kwargs):
        if df.empty: return

        if len(df.columns) > 0:
            self._df = df
        else:
            raise AttributeError(f" [X] No columns!")

    def __call__(self, kind=None, alias=None, timed=False, **kwargs):
        try:
            if isinstance(kind, str):
                kind = kind.lower() 
                fn = getattr(self, kind)

                if timed:
                    stime = time.time()

                # Run the indicator
                indicator = fn(**kwargs)

                if timed:
                    time_diff = time.time() - stime
                    ms = time_diff * 1000
                    indicator.timed = f"{ms:2.3f} ms ({time_diff:2.3f} s)"
                    # print(f"execution time: {indicator.timed}")

                # Add an alias if passed
                if alias:
                    indicator.alias = f"{alias}"
                
                return indicator
            else:
                self.help()

        except:
            self.help()



    def _append(self, result=None, **kwargs):
        """Appends a Pandas Series or DataFrame columns to self._df."""
        if 'append' in kwargs and kwargs['append']:
            df = self._df
            if df is None or result is None: return
            else:                
                if isinstance(result, pd.DataFrame):
                    for i, column in enumerate(result.columns):
                        df[column] = result.iloc[:,i]
                else:
                    df[result.name] = result


    def _get_column(self, series, default):
        """Attempts to get the correct series or 'column' and return it."""
        df = self._df
        if df is None: return

        # Explicit passing a pd.Series to override default.
        if isinstance(series, pd.Series):
            return series

        # Apply default if no series.
        elif (series is None) and (default in df.columns):
            return df[default]

        # Ok.  So it's a str.
        elif isinstance(series, str):
            # Return the df column since it's in there.
            if series in df.columns:
                return df[series]
            else:
                # Attempt to match the 'series' because it was likely misspelled.
                matches = df.columns.str.match(series, case=False)
                match = [i for i, x in enumerate(matches) if x]
                # If found, awesome.  Return it or return the 'series'.
                cols = ', '.join(list(df.columns))
                NOT_FOUND = f" [X] Ooops!!!: It's {series not in df.columns}, the series '{series}' not in {cols}"
                return df.iloc[:,match[0]] if len(match) else print(NOT_FOUND)


    def constants(self, apply, lower_bound=-100, upper_bound=100, every=1):
        """Constants

        Useful for indicator levels or if you need some constant value.

        Add constant '1' to the DataFrame
        >>> df.ta.constants(True, 1, 1, 1)
        Remove constant '1' to the DataFrame
        >>> df.ta.constants(False, 1, 1, 1)

        Adding constants that range of constants from -4 to 4 inclusive
        >>> df.ta.constants(True, -4, 4, 1)
        Removing constants that range of constants from -4 to 4 inclusive
        >>> df.ta.constants(False, -4, 4, 1)

        Args:
            apply (bool): Default: None.  If True, appends the range of constants to the
                working DataFrame.  If False, it removes the constant range from the working
                DataFrame.
            lower_bound (int): Default: -100.  Lowest integer for the constant range.
            upper_bound (int): Default: 100.  Largest integer for the constant range.
            every (int): Default: 10.  How often to include a new constant.
        
        Returns:
            Returns nothing to the user.  Either adds or removes constant ranges from the
            working DataFrame.
        """
        levels = [x for x in range(lower_bound, upper_bound + 1) if x % every == 0]
        if apply:
            for x in levels:
                self._df[f'{x}'] = x
        else:
            for x in levels:
                del self._df[f'{x}']


    def indicators(self, **kwargs):
        """Indicator list"""
        header = f"pandas.ta - Technical Analysis Indicators"
        helper_methods = ['indicators', 'constants']  # Public non-indicator methods
        ta_properties = ['adjusted']
        exclude_methods = kwargs.pop('exclude', None)
        as_list = kwargs.pop('as_list', False)
        ta_indicators = list((x for x in dir(pd.DataFrame().ta) if not x.startswith('_') and not x.endswith('_')))

        for x in helper_methods:
            ta_indicators.remove(x)

        for x in ta_properties:
            ta_indicators.remove(x)

        if isinstance(exclude_methods, list) and exclude_methods in ta_indicators and len(exclude_methods) > 0:
            for x in exclude_methods:
                ta_indicators.remove(x)

        if as_list:
            return ta_indicators

        total_indicators = len(ta_indicators)
        s = f"{header}\nTotal Indicators: {total_indicators}\n"
        if total_indicators > 0:            
            abbr_list = ', '.join(ta_indicators)
            print(f"{s}Abbreviations:\n    {abbr_list}")
        else:
            print(s)

    # Hyb Indicators
    def fractal(self, high=None, low=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from .hyb.fractal import fractal
        result = fractal(high=high, low=low, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    # Momentum Indicators
    def ao(self, high=None, low=None, fast=None, slow=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from .momentum.ao import ao
        result = ao(high=high, low=low, fast=fast, slow=slow, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def apo(self, close=None, fast=None, slow=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.apo import apo
        result = apo(close=close, fast=fast, slow=slow, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def bop(self, open_=None, high=None, low=None, close=None, percentage=False, offset=None, **kwargs):
        open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.bop import bop
        result = bop(open_=open_, high=high, low=low, close=close, percentage=percentage, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def cci(self, high=None, low=None, close=None, length=None, c=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.cci import cci
        result = cci(high=high, low=low, close=close, length=length, c=c, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def cg(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.cg import cg
        result = cg(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def cmo(self, close=None, length=None, drift=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.cmo import cmo
        result = cmo(close=close, length=length, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def coppock(self, close=None, length=None, fast=None, slow=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.coppock import coppock
        result = coppock(close=close, length=length, fast=fast, slow=slow, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def fisher(self, high=None, low=None, length=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from .momentum.fisher import fisher
        result = fisher(high=high, low=low, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def kst(self, close=None, roc1=None, roc2=None, roc3=None, roc4=None, sma1=None, sma2=None, sma3=None, sma4=None, signal=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.kst import kst
        result = kst(close=close, roc1=roc1, roc2=roc2, roc3=roc3, roc4=roc4, sma1=sma1, sma2=sma2, sma3=sma3, sma4=sma4, signal=signal, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def macd(self, close=None, fast=None, slow=None, signal=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.macd import macd
        result = macd(close=close, fast=fast, slow=slow, signal=signal, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def mom(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.mom import mom
        result = mom(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def ppo(self, close=None, fast=None, slow=None, percentage=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.ppo import ppo
        result = ppo(close=close, fast=fast, slow=slow, percentage=percentage, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def roc(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.roc import roc
        result = roc(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def rsi(self, close=None, length=None, drift=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.rsi import rsi
        result = rsi(close=close, length=length, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def rvi(self, open_=None, high=None, low=None, close=None, length=None, swma_length=None, offset=None, **kwargs):
        open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.rvi import rvi
        result = rvi(open_=open_, high=high, low=low, close=close, length=length, swma_length=swma_length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def slope(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.slope import slope
        result = slope(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def stoch(self, high=None, low=None, close=None, fast_k=None, slow_k=None, slow_d=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.stoch import stoch
        result = stoch(high=high, low=low, close=close, fast_k=fast_k, slow_k=slow_k, slow_d=slow_d, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def trix(self, close=None, length=None, drift=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.trix import trix
        result = trix(close=close, length=length, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def tsi(self, close=None, fast=None, slow=None, drift=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .momentum.tsi import tsi
        result = tsi(close=close, fast=fast, slow=slow, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def uo(self, high=None, low=None, close=None, fast=None, medium=None, slow=None, fast_w=None, medium_w=None, slow_w=None, drift=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.uo import uo
        result = uo(high=high, low=low, close=close, fast=fast, medium=medium, slow=slow, fast_w=fast_w, medium_w=medium_w, slow_w=slow_w, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def willr(self, high=None, low=None, close=None, length=None, percentage=True, offset=None,**kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .momentum.willr import willr
        result = willr(high=high, low=low, close=close, length=length, percentage=percentage, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    # Overlap Indicators
    def dema(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.dema import dema
        result = dema(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def ema(self, close=None, length=None, offset=None, adjust=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.ema import ema
        result = ema(close=close, length=length, offset=offset, adjust=adjust, **kwargs)
        self._append(result, **kwargs)
        return result

    def fwma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.fwma import fwma
        result = fwma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def hl2(self, high=None, low=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from .overlap.hl2 import hl2
        result = hl2(high=high, low=low, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def hlc3(self, high=None, low=None, close=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .overlap.hlc3 import hlc3
        result = hlc3(high=high, low=low, close=close, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def hma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.hma import hma
        result = hma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def kama(self, close=None, length=None, fast=None, slow=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.kama import kama
        result = kama(close=close, length=length, fast=fast, slow=slow, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def ichimoku(self, high=None, low=None, close=None, tenkan=None, kijun=None, senkou=None, offset=None, **kwargs):        
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .overlap.ichimoku import ichimoku
        result, span = ichimoku(high=high, low=low, close=close, tenkan=tenkan, kijun=kijun, senkou=senkou, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result, span

    def linreg(self, close=None, length=None, offset=None, adjust=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.linreg import linreg
        result = linreg(close=close, length=length, offset=offset, adjust=adjust, **kwargs)
        self._append(result, **kwargs)
        return result

    def midpoint(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.midpoint import midpoint
        result = midpoint(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def midprice(self, high=None, low=None, length=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from .overlap.midprice import midprice
        result = midprice(high=high, low=low, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def ohlc4(self, open_=None, high=None, low=None, close=None, offset=None, **kwargs):
        open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .overlap.ohlc4 import ohlc4
        result = ohlc4(open_=open_, high=high, low=low, close=close, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def pwma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.pwma import pwma
        result = pwma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def rma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.rma import rma
        result = rma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def sinwma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.sinwma import sinwma
        result = sinwma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def sma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.sma import sma
        result = sma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def swma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.swma import swma
        result = swma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def t3(self, close=None, length=None, a=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.t3 import t3
        result = t3(close=close, length=length, a=a, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def tema(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.tema import tema
        result = tema(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def trima(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.trima import trima
        result = trima(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def vwap(self, high=None, low=None, close=None, volume=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from .overlap.vwap import vwap
        result = vwap(high=high, low=low, close=close, volume=volume, offset=offset, **kwargs)
        self._append(result, **kwargs)        
        return result

    def vwma(self, close=None, volume=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from .overlap.vwma import vwma
        result = vwma(close=close, volume=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def wma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.wma import wma
        result = wma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def zlma(self, close=None, length=None, offset=None, mamode=None, **kwargs):
        close = self._get_column(close, 'close')
        from .overlap.zlma import zlma
        result = zlma(close=close, length=length, offset=offset, mamode=mamode, **kwargs)
        self._append(result, **kwargs)
        return result


    # Performance Indicators
    def log_return(self, close=None, length=None, cumulative=False, percent=False, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from pandas_ta.performance.log_return import log_return
        result = log_return(close=close, length=length, cumulative=cumulative, percent=percent, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def percent_return(self, close=None, length=None, cumulative=False, percent=False, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from pandas_ta.performance.percent_return import percent_return
        result = percent_return(close=close, length=length, cumulative=cumulative, percent=percent, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def trend_return(self, close=None, trend=None, log=True, cumulative=None, offset=None, trend_reset=None, **kwargs):
        close = self._get_column(close, 'close')
        trend = self._get_column(trend, f"{trend}")
        from pandas_ta.performance.trend_return import trend_return
        result = trend_return(close=close, trend=trend, log=log, cumulative=cumulative, offset=offset, trend_reset=trend_reset, **kwargs)
        self._append(result, **kwargs)
        return result


    # Statistics Indicators
    def kurtosis(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.kurtosis import kurtosis
        result = kurtosis(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def mad(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.mad import mad
        result = mad(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def median(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.median import median
        result = median(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def quantile(self, close=None, length=None, q=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.quantile import quantile
        result = quantile(close=close, length=length, q=q, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def skew(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.skew import skew
        result = skew(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def stdev(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.stdev import stdev
        result = stdev(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def variance(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.variance import variance
        result = variance(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def zscore(self, close=None, length=None, std=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .statistics.zscore import zscore
        result = zscore(close=close, length=length, std=std, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result



    # Trend Indicators
    def adx(self, high=None, low=None, close=None, drift=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .trend.adx import adx
        result = adx(high=high, low=low, close=close, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def amat(self, close=None, fast=None, slow=None, mamode=None, lookback=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.amat import amat
        result = amat(close=close, fast=fast, slow=slow, mamode=mamode, lookback=lookback, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def aroon(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.aroon import aroon
        result = aroon(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def decreasing(self, close=None, length=None, asint=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.decreasing import decreasing
        result = decreasing(close=close, length=length, asint=asint, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def dpo(self, close=None, length=None, centered=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.dpo import dpo
        result = dpo(close=close, length=length, centered=centered, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def increasing(self, close=None, length=None, asint=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.increasing import increasing
        result = increasing(close=close, length=length, asint=asint, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def linear_decay(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from .trend.linear_decay import linear_decay
        result = linear_decay(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def long_run(self, fast=None, slow=None, length=None, offset=None, **kwargs):
        if fast is None and slow is None: return self._df
        else:
            fast = self._get_column(fast, f"{fast}")
            slow = self._get_column(slow, f"{slow}")
            from .trend.long_run import long_run
            result = long_run(fast=fast, slow=slow, length=length, offset=offset, **kwargs)
            self._append(result, **kwargs)
            return result

    def qstick(self, open_=None, close=None, length=None, offset=None, **kwargs):
        open_ = self._get_column(open_, 'open')
        close = self._get_column(close, 'close')
        from .trend.qstick import qstick
        result = qstick(open_=open_, close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def short_run(self, fast=None, slow=None, length=None, offset=None, **kwargs):
        if fast is None and slow is None: return self._df
        else:
            fast = self._get_column(fast, f"{fast}")
            slow = self._get_column(slow, f"{slow}")
            from .trend.short_run import short_run
            result = short_run(fast=fast, slow=slow, length=length, offset=offset, **kwargs)
            self._append(result, **kwargs)
            return result

    def vortex(self, high=None, low=None, close=None, drift=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from .trend.vortex import vortex
        result = vortex(high=high, low=low, close=close, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result



    # Utility Indicators
    def cross(self, a=None, b=None, above=True, asint=True, offset=None, **kwargs):
        if a is None and b is None: return self._df
        else:
            a = self._get_column(a, f"{a}")
            b = self._get_column(b, f"{b}")
            result = cross(series_a=a, series_b=b, above=above, asint=asint, offset=offset, **kwargs)
            self._append(result, **kwargs)
            return result



    # Volatility Indicators
    def accbands(self, high=None, low=None, close=None, length=None, c=None, mamode=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.accbands import accbands
        result = accbands(high=high, low=low, close=close, length=length, c=c, mamode=mamode, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def atr(self, high=None, low=None, close=None, length=None, mamode=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.atr import atr
        result = atr(high=high, low=low, close=close, length=length, mamode=mamode, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def bbands(self, close=None, length=None, stdev=None, mamode=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.bbands import bbands
        result = bbands(close=close, length=length, stdev=stdev, mamode=mamode, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def donchian(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.donchian import donchian
        result = donchian(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def kc(self, high=None, low=None, close=None, length=None, scalar=None, mamode=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.kc import kc
        result = kc(high=high, low=low, close=close, length=length, scalar=scalar, mamode=mamode, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def massi(self, high=None, low=None, fast=None, slow=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        from pandas_ta.volatility.massi import massi
        result = massi(high=high, low=low, fast=fast, slow=slow, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def natr(self, high=None, low=None, close=None, length=None, mamode=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.natr import natr
        result = natr(high=high, low=low, close=close, length=length, mamode=mamode, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def true_range(self, high=None, low=None, close=None, drift=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        from pandas_ta.volatility.true_range import true_range
        result = true_range(high=high, low=low, close=close, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result



    # Volume Indicators
    def ad(self, high=None, low=None, close=None, volume=None, open_=None, signed=True, offset=None, **kwargs):
        if open_ is not None:
            open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.ad import ad
        result = ad(high=high, low=low, close=close, volume=volume, open_=open_, signed=signed, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def adosc(self, high=None, low=None, close=None, volume=None, open_=None, fast=None, slow=None, signed=True, offset=None, **kwargs):
        if open_ is not None:
            open_ = self._get_column(open_, 'open')        
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.adosc import adosc
        result = adosc(high=high, low=low, close=close, volume=volume, open_=open_, fast=fast, slow=slow, signed=signed, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def aobv(self, close=None, volume=None, fast=None, slow=None, mamode=None, max_lookback=None, min_lookback=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.aobv import aobv
        result = aobv(close=close, volume=volume, fast=fast, slow=slow, mamode=mamode, max_lookback=max_lookback, min_lookback=min_lookback, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def cmf(self, high=None, low=None, close=None, volume=None, open_=None, length=None, offset=None, **kwargs):
        if open_ is not None:
            open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.cmf import cmf
        result = cmf(high=high, low=low, close=close, volume=volume, open_=open_, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def efi(self, close=None, volume=None, length=None, mamode=None, offset=None, drift=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.efi import efi
        result = efi(close=close, volume=volume, length=length, offset=offset, mamode=mamode, drift=drift, **kwargs)
        self._append(result, **kwargs)
        return result

    def eom(self, high=None, low=None, close=None, volume=None, length=None, divisor=None, offset=None, drift=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.eom import eom
        result = eom(high=high, low=low, close=close, volume=volume, length=length, divisor=divisor, offset=offset, drift=drift, **kwargs)
        self._append(result, **kwargs)
        return result

    def mfi(self, high=None, low=None, close=None, volume=None, length=None, drift=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.mfi import mfi
        result = mfi(high=high, low=low, close=close, volume=volume, length=length, drift=drift, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def nvi(self, close=None, volume=None, length=None, initial=None, signed=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.nvi import nvi
        result = nvi(close=close, volume=volume, length=length, initial=initial, signed=signed, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def obv(self, close=None, volume=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.obv import obv
        result = obv(close=close, volume=volume, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def pvi(self, close=None, volume=None, length=None, initial=None, signed=True, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.pvi import pvi
        result = pvi(close=close, volume=volume, length=length, initial=initial, signed=signed, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def pvol(self, close=None, volume=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.pvol import pvol
        result = pvol(close=close, volume=volume, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def pvt(self, close=None, volume=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.pvt import pvt
        result = pvt(close=close, volume=volume, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result

    def vp(self, close=None, volume=None, width=None, percent=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        from pandas_ta.volume.vp import vp
        return vp(close=close, volume=volume, width=width, percent=percent, **kwargs)
