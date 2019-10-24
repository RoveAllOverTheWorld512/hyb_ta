# coding: utf8

# part of pybacktest package: https://github.com/ematvey/pybacktest


import time

from cached_property import cached_property
import pybacktest.performance
import pybacktest.parts
import pandas


__all__ = ['Backtest']


class StatEngine(object):
    def __init__(self, equity_fn):
        self._stats = [i for i in dir(pybacktest.performance) if not i.startswith('_')]
        self._equity_fn = equity_fn

    def __dir__(self):
        return dir(type(self)) + self._stats

    def __getattr__(self, attr):
        if attr in self._stats:
            equity = self._equity_fn()
            fn = getattr(pybacktest.performance, attr)
            try:
                return fn(equity)
            except:
                return
        else:
            raise IndexError(
                "Calculation of '%s' statistic is not supported" % attr)


class Backtest(object):
    """
    Backtest (Pandas implementation of vectorized backtesting).

    Lazily attempts to extract multiple pandas.Series with signals and prices
    from a given namespace and combine them into equity curve.

    Attempts to be as smart as possible.

    """

    _ohlc_possible_fields = ('ohlc', 'bars', 'ohlcv')
    _sig_mask_int = ('Buy', 'Sell', 'Short', 'Cover')
    _pr_mask_int = ('BuyPrice', 'SellPrice', 'ShortPrice', 'CoverPrice')

    def __init__(self, dataobj, name='Unknown',
                 signal_fields=('buy', 'sell', 'short', 'cover'),
                 price_fields=('buyprice', 'sellprice', 'shortprice',
                               'coverprice')):
        """
        Arguments:

        *dataobj* should be dict-like structure containing signal series.
        Easiest way to define is to create pandas.Series with exit and entry
        signals and pass whole local namespace (`locals()`) as dataobj.

        *name* is simply backtest/strategy name. Will be user for printing,
        potting, etc.

        *signal_fields* specifies names of signal Series that backtester will
        attempt to extract from dataobj. By default follows AmiBroker's naming
        convention.

        *price_fields* specifies names of price Series where trades will take
        place. If some price is not specified (NaN at signal's timestamp, or
        corresponding Series not present in dataobj altogather), defaults to
        Open price of next bar. By default follows AmiBroker's naming
        convention.

        Also, dataobj should contain dataframe with Bars of underlying
        instrument. We will attempt to guess its name before failing miserably.

        To get a hang of it, check out the examples.

        """
        self._dataobj = dict([(k.lower(), v) for k, v in dataobj.items()])
        self._sig_mask_ext = signal_fields
        self._pr_mask_ext = price_fields
        self.name = name
        self.run_time = time.strftime('%Y-%d-%m %H:%M %Z', time.localtime())
        self.stats = StatEngine(lambda: self.equity)

    def __repr__(self):
        return "Backtest(%s, %s)" % (self.name, self.run_time)

    @property
    def dataobj(self):
        return self._dataobj

    @cached_property
    def signals(self):
        return pybacktest.parts.extract_frame(self.dataobj, self._sig_mask_ext,
                                              self._sig_mask_int).fillna(value=False)

    @cached_property
    def prices(self):
        return pybacktest.parts.extract_frame(self.dataobj, self._pr_mask_ext,
                                              self._pr_mask_int)

    @cached_property
    def default_price(self):
        return self.ohlc.O  # .shift(-1)

    @cached_property
    def trade_price(self):
        pr = self.prices
        if pr is None:
            return self.ohlc.O  # .shift(-1)
        dp = pandas.Series(dtype=float, index=pr.index)
        for pf, sf in zip(self._pr_mask_int, self._sig_mask_int):
            s = self.signals[sf]
            p = self.prices[pf]
            dp[s] = p[s]
        return dp.combine_first(self.default_price)

    @cached_property
    def positions(self):
        return pybacktest.parts.signals_to_positions(self.signals,
                                                     mask=self._sig_mask_int)

    @cached_property
    def trades(self):
        p = self.positions.reindex(
            self.signals.index).ffill().shift().fillna(value=0)
        p = p[p != p.shift()]
        tp = self.trade_price
        assert p.index.tz == tp.index.tz, "Cant operate on singals and prices " \
                                          "indexed as of different timezones"
        t = pandas.DataFrame({'pos': p})
        t['price'] = tp
        t = t.dropna()
        t['vol'] = t.pos.diff()
        return t.dropna()

    @cached_property
    def equity(self):
        return pybacktest.parts.trades_to_equity(self.trades)

    @cached_property
    def ohlc(self):
        for possible_name in self._ohlc_possible_fields:
            s = self.dataobj.get(possible_name)
            if s is not None:
                return s
        raise Exception("Bars dataframe was not found in dataobj")

    @cached_property
    def report(self):
        return pybacktest.performance.performance_summary(self.equity)

    def summary(self):
        import yaml

        s = '|  %s  |' % self
        print('-' * len(s))
        print(s)
        print('-' * len(s) + '\n')
        print(yaml.dump(self.report, allow_unicode=True, default_flow_style=False))
        print('-' * len(s))

    def plot_equity(self, ax=None):
        import matplotlib.pylab as pylab
        _ = None
        if ax is None:
            _, ax = pylab.subplots()

        self.ohlc['eq'] = self.equity
        eq = self.ohlc['eq'].fillna(value=0)
        eq = eq.cumsum()
        eq.plot(color='red', style='-', ax=ax)
        ax.legend(loc='best')
        ax.set_ylabel('Equity')
        return _, ax

    def plot_trades(self, ax=None):
        fr = self.trades
        le = fr.price[(fr.pos > 0) & (fr.vol > 0)]
        se = fr.price[(fr.pos < 0) & (fr.vol < 0)]
        lx = fr.price[(fr.pos.shift() > 0) & (fr.vol < 0)]
        sx = fr.price[(fr.pos.shift() < 0) & (fr.vol > 0)]

        import matplotlib.pylab as pylab
        _ = None
        if ax is None:
            _, ax = pylab.subplots()

        self.ohlc.O.plot(color='black', label='price', ax=ax)

        ax.plot(le.index, le.values, '^', color='red', markersize=8,
                label='long enter')
        ax.plot(se.index, se.values, 'v', color='lime', markersize=8,
                label='short enter')
        ax.plot(lx.index, lx.values, 'o', color='red', markersize=8,
                label='long exit')
        ax.plot(sx.index, sx.values, 'o', color='lime', markersize=8,
                label='short exit')
        ax.legend(loc='best')
        ax.set_ylabel('Trades')
        return _, ax
