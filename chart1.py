# -*- coding: utf-8 -*-
"""
Created on 2019-10-08 15:05:21

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

绘制蜡烛图、成交量和指标（可选，如技术指标或交易信号）

"""

import matplotlib.dates as mdates
import mpl_finance as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta
import datetime

def candlestick(df, **kwargs):
    """
    绘制和保存（可选）DataFrame数据源的蜡烛图
    参数：
    df : DataFrame，按顺序保存'datetime'(index),'open', 'high', 'low', 'close'和'volume'列
    title : str, 可选
    fname : str, 可选，'.png' or '.pdf'后缀的图片名
    events : DataFrame, 可选，与df相同index，最多四列，无事件则用np.nan
    macd: DataFrame，与df相同index，
    band : DataFrame, 可选，需要包含'upper'和'lower'两列，例如布林带指标
    lines : DataFrame, 可选，例如移动平均线
    """
    _make_chart(df, _candlestick_ax, **kwargs)


def close(df, **kwargs):
    """
    绘制和保存（可选）收盘价
    """
    _make_chart(df, _close_ax, **kwargs)


def _make_chart(df, chartfn, **kwargs):

    N = len(df)
    mdate = df['date']
    def format_date(x, pos=None):
        thisind = np.clip(int(x + 0.5 - mdates.datestr2num(df.iloc[0]['date'])), 0, N - 1)
        return mdate.iloc[thisind]

    fig = plt.figure(figsize=(24, 12))
    # 6行4列，左上角为0，0

    # 画K线
    ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=4, colspan=4)
    ax1.grid(True)
    plt.ylabel('Price')
    # gca-->Get Current Axes
    # 设置x刻度标签不可见
#    ax1.xaxis.set_visible(False)
    plt.setp(plt.gca().get_xticklabels(), visible=False)
    chartfn(df, ax1)
    if 'lines' in kwargs:
        _plot_lines(kwargs['lines'])
    if 'band' in kwargs:
        _plot_band(kwargs['band'])
    if 'events' in kwargs:
        _plot_events(kwargs['events'])

    # 画成交量，与K线共X轴
    ax2 = plt.subplot2grid((6, 4), (4, 0), sharex=ax1, rowspan=1, colspan=4)
    volume = df['volume']
    pos = df['open'] - df['close'] <= 0  # mask
    neg = df['open'] - df['close'] > 0
    ax2.bar(volume[pos].index, volume[pos], color='red', width=0.4, align='center')
    ax2.bar(volume[neg].index, volume[neg], color='green', width=0.4, align='center')

    ax2.grid(True)
    plt.ylabel('Volume')
#    ax2.xaxis.set_visible(False)
  
    # 画指标
    ax3 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4)
    macd = get_macd(df)
    plt.plot(macd.index, macd.iloc[:, 0].values, 'k')
    plt.plot(macd.index, macd.iloc[:, 1].values, 'b')
    macdh = macd.iloc[:,2]
    pos = macdh > 0  # mask
    neg = macdh < 0  # mask
    ax3.bar(macdh[pos].index, macdh[pos], color='red', width=0.4, align='center')
    ax3.bar(macdh[neg].index, macdh[neg], color='green', width=0.4, align='center')

    plt.xlabel('Date')
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    ax3.xaxis.set_major_locator(mticker.MaxNLocator(16))
    fmt = mticker.FuncFormatter(format_date)
    ax3.xaxis.set_major_formatter(fmt)
    if len(df.index) <= 500:
        ax3.xaxis.set_minor_locator(mdates.DayLocator())

    ax3.grid(True)
    ax3.set_ylabel('MACD')

    plt.subplots_adjust(left=.09, bottom=.18, right=.94, top=0.94, wspace=.20, hspace=0)
    if 'title' in kwargs:
        plt.suptitle(kwargs['title'])
    if 'fname' in kwargs:
        plt.savefig(kwargs['fname'], bbox_inches='tight')
    plt.show()
    # plt.close()


def _candlestick_ax(df, ax):
    columns = ['date_num', 'open', 'high', 'low', 'close']
    quotes = df[columns]
    fplt.candlestick_ohlc(ax, quotes.values, width=0.4, colorup='red', colordown='green')


def _close_ax(df, ax):
    ax.plot(df.index, df.loc[:, 'close'])


def _plot_band(band):
    plt.fill_between(band.index, band.loc[:, 'upper'].values,
                     band.loc[:, 'lower'].values, facecolor='gray', alpha=0.5)


def _plot_lines(lines):
    colors = ['b', 'r', 'g']
    n_lines = min(len(lines.columns), len(colors))
    for i in range(n_lines):
        plt.plot(lines.index, lines.iloc[:, i].values, colors[i])


def _plot_events(events):
    colors = ['m^', 'bv', 'rD', 'gd']
    n_events = min({len(events.columns), len(colors)})
    for i in range(n_events):
        plt.plot(events.index, events.iloc[:, i].values, colors[i], ms=8.0)


def _plot_tracks(tracks):
    colors = ['r', 'b']
    n_tracks = min({len(tracks.columns), len(colors)})
    for i in range(n_tracks):
        ob = tracks.iloc[:, i].values
        plt.plot(tracks.index, ob, colors[i], lw=0.5)
        plt.ylim(((1.1 if min(ob) < 0 else -1.1) * min(ob), 1.1 * max(ob)))
        if min(ob) < 0 < max(ob):
            plt.axhline(y=0.0, color='k', lw=0.5)


def add_datenum(df, start=None, end=None):
    try:
        start = pd.to_datetime(start)
    except ValueError:
        start = None
    try:
        end = pd.to_datetime(end)
    except ValueError:
        end = None
    if not start:
        start = df.index[0]
    if not end:
        end = df.index[-1]
    df = df[start:end]

    df = df.sort_index()  # 索引为date，按日期时间升序排序
    df = df.reset_index()  # 将date变为一列
    df = df.reset_index()  # 将序号变为一列index
    df['date'] = df['date'].map(lambda x: x.strftime('%Y-%m-%d'))
    df['date_num'] = df['index'] + mdates.datestr2num(df.iloc[0]['date'])
    df = df.drop(columns=['index'])
    df = df.set_index('date_num', drop=False)
    return df


def get_macd(df):
    columns = []
    for col in ['macd_', 'macds_', 'macdh_']:
        matches = df.columns.str.match(col, case=False)
        match = [i for i, x in enumerate(matches) if x]
        if len(match) != 1:
            print('macd指标有误')
            return None
        columns.append(df.columns[match[0]])
    return df[columns]


def nd_today(n):
    '''
    返回n天前到今天的日期
    '''
    today = datetime.datetime.now()
    ndtoday = today + datetime.timedelta(-n)
    return ndtoday.strftime("%Y%m%d"), today.strftime("%Y%m%d")


if __name__ == '__main__':
    filename = '000651'
    tdxday = Tdxday(filename)
#    stock = tdxday.get_data_yahoo(start='20180101')
#    stock = tdxday.get_qfqdata(start='20180101', otype='ohlc')
#    stock = tdxday.get_data_backtrader(start='20180101')
#    scdm = stock.scdm
#    stock.to_csv(f"{scdm}{filename}.csv")

    stock = tdxday.get_qfqdata(start='20180101')
    stock.ta.alligator(append=True)
    stock.ta.macd(append=True)
    stock.ta.fractals(append=True)
    stock.ta.bottomreversal(append=True)
    start = '20180501'
    end = '20181231'
    start, end = nd_today(180)
    stock = add_datenum(stock, start=start, end=end)
    lines = stock[['ALLIGATOR_JAW_13_8', 'ALLIGATOR_TEETH_8_5',
                   'ALLIGATOR_LIPS_5_3']]
    fx = stock[['FRACTAL_UPPRICE', 'FRACTAL_DOWNPRICE', 'BOTTOM_REVERSAL_LOW']]
    fx = fx.assign(FRACTAL_UPPRICE=fx['FRACTAL_UPPRICE']*1.02)
    fx = fx.assign(FRACTAL_DOWNPRICE=fx['FRACTAL_DOWNPRICE']*0.98)
    fx = fx.assign(BOTTOM_REVERSAL_LOW=fx['BOTTOM_REVERSAL_LOW']*0.90)
    pngfn = f'{filename}_{start}_{end}.png'
    candlestick(stock, lines=lines, events=fx, title=filename, fname=pngfn)

    close(stock, fname='tmp.png')