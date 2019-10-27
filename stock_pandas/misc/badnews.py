# -*- coding: utf-8 -*-
"""
Created on 2019-10-27 11:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

bad news 利空走势分析
分析方法：利空点前三个月的高点，后三个月的低点，低点后一个月反弹的高点
"""

import pandas as pd
from numpy import NaN as npNaN
from math import isnan
import dateutil.parser

def idxmax(ds, i, l):
    '''
    返回pandas.Series指定位置、指定区间内的最大值及索引
    注意：ds索引号为顺序号，l>0
    '''
    if isnan(i):
        return None
    if (l <= 0) | ((i - l + 1) < 0) | (i > len(ds)):
        return None
    s = ds.iloc[(i - l + 1): i + 1]
    return s.loc[[s.idxmax()]]

def idxmin(ds, i, l):
    '''
    返回pandas.Series指定位置、指定区间内的最小值及索引
    注意：ds索引号为顺序号，l>0
    '''
    if isnan(i):
        return None
    if (l <= 0) | ((i - l + 1) < 0) | (i > len(ds)):
        return None
#    print(f'i={i}')
    s = ds.iloc[(i - l + 1): i + 1]
    return s.loc[[s.idxmin()]]


def badnews(df, date, j=60, k=60, l=30, m=120):
    '''
    利空走势分析：利空发生日前j个交易日内（含消息日）高点，
    利空发生日后k个交易日内（不含消息日）低点
    低点后l个交易日内（不含低点日）高点
    '''
    df = df.sort_index()  # 按索引date排序
    dt = dateutil.parser.parse(date)
    df = df.reset_index()  # 将索引date变成一列
    i = df.loc[(df['date'] >= dt)].index[0] - 1  # 对应索引序号
    # 由于有可能日期不在序列中，所以要用“>=”
    p = df.loc[i, 'close']  # 对应收盘价
    dt = df['date'].iloc[i].strftime('%Y%m%d')
    ds = df['close']
    if i < j -1:  # 前面交易天数不够
        j = i + 1
    p0 = idxmax(ds, i, j)  # 获取前高点信息
    p0i = p0.index[0]  # 前高点索引序号
    p0v = p0.loc[p0i]  # 前高点价格
    p0d = df['date'].iloc[p0i].strftime('%Y%m%d')  # 前高点日期
    p0ds = i - p0i   # 距前高点交易日天数
    p0zf = p / p0v - 1  # 前期跌幅
    if i + k > len(ds):  # 后面交易天数不够
        k = len(ds) - 1 - i
    p1 = idxmin(ds, i + k, k)  # 获取后低点信息
    p1i = p1.index[0]
    p1v = p1.loc[p1i]
    p1d = df['date'].iloc[p1i].strftime('%Y%m%d')
    p1ds = p1i - i
    p1zf = p1v / p - 1
    if p1i + l > len(ds):  # 后面天数不够
        l = len(ds) - 1 - p1i
    p2 = idxmax(ds, p1i + l, l)
    if p2 is not None:
        p2i = p2.index[0]
        p2v = p2.loc[p2i]
        p2d = df['date'].iloc[p2i].strftime('%Y%m%d')
        p2ds = p2i - i
        p2zf = p2v / p1v - 1
    else:
        p2i = None
        p2v = None
        p2d = None
        p2ds = None
        p2zf = None
    if i + m > len(ds):  # 后面交易天数不够
        m = len(ds) - 1 - i
    p3 = idxmin(ds, i + m, m)  # 获取后低点信息
    p3i = p3.index[0]
    p3v = p3.loc[p3i]
    p3d = df['date'].iloc[p3i].strftime('%Y%m%d')
    p3ds = p3i - i
    p3zf = p3v / p - 1

    return [p0d, p0ds, p0v, p0zf, dt, p, p1d, p1ds, p1v, p1zf, p2d, p2ds, p2v, p2zf, p3d, p3ds, p3v, p3zf]


