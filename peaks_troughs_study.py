# -*- coding: utf-8 -*-
"""
Created on 2019-10-17 21:21:35

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import sys


def best_peaks_troughs(peaks, troughs, pv, tv):
    '''
    pv:有效涨幅阈值，如0.2表示上涨幅度超过20%
    tv:有效回撤阈值，如0.2表示回撤幅度大于20%
    '''
#    pv=0.2
#    tv=0.2

    pt = []
    for i in peaks.index:
        pt.append((i, peaks[i]))
    for i in troughs.index:
        pt.append((i, troughs[i]))
    pt.sort(key=lambda x: x[0])

    start = pt[0]
    end = pt[-1]

    # 去掉上升中继和下跌中继
    i = 2
    while i < len(pt) - 1 and len(pt) > 4:

        if i < 2:
            i = 2
        p0 = pt[i-2]
        p1 = pt[i-1]
        p2 = pt[i]
        p3 = pt[i+1]

        if ((p1[1] > p0[1]) and (p2[1] < p1[1])
            and (p3[1] > p2[1]) and (p2[1] >= p0[1])
                and (p3[1] > p1[1])):
            # 4点N形上升通道情形一:下两点后点高于或等于前点，上两点后点高于前点
            zf = abs(p2[1] / p1[1] - 1)     # 回调幅度
            # 回调幅度小于设定阈值，则删除中间两点，指针回调2
            # 回调幅度大于等于于设定阈值，指针前进1
            if (zf < tv):
                pt.remove(p1)
                pt.remove(p2)
                i -= 2
            else:
                i += 1
        elif ((p1[1] > p0[1]) and (p2[1] < p1[1])
                and (p3[1] > p2[1]) and (p2[1] >= p0[1])
                and (p3[1] <= p1[1])):
            # 4点N形上升通道情形二:下两点后点高于或等于前点，上两点后点低于或等于前点
            zf = abs(p2[1]/p1[1]-1)     # 回调幅度
            # 回调幅度小于设定阈值，则删除后面两点，指针回调2
            # 回调幅度大于等于于设定阈值，指针前进1
            if (zf<tv):
                pt.remove(p2)
                pt.remove(p3)
                i -= 2
            else:
                i += 1
        elif ((p1[1] < p0[1]) and (p2[1] > p1[1])
                and (p3[1] < p2[1]) and (p2[1] <= p0[1])
                and (p3[1] < p1[1])):
            # 4点倒N(VI)形下降通道情形一:上两点后点低于或等于前点，下两点后点低于于前点
            zf = abs(p2[1] / p1[1] - 1)     # 上升幅度
            # 上涨幅度小于设定阈值，则删除中间两点，指针回调2
            # 上涨幅度大于等于于设定阈值，指针前进1
            if (zf < pv):
                pt.remove(p1)
                pt.remove(p2)
                i -= 2
            else:
                i += 1
        elif ((p1[1] < p0[1]) and (p2[1] > p1[1])
                and (p3[1] < p2[1]) and (p2[1] <= p0[1])
                and (p3[1] >= p1[1])):
            # 4点倒N(VI)形下降通道情形二:上两点后点低于或等于前点，下两点后点高于或等于于前点
            zf = abs(p2[1] / p1[1] - 1)     #上涨幅度
            # 上涨幅度小于设定阈值，则删除后面两点，指针回调2
            # 上涨幅度大于等于于设定阈值，指针前进1
            if (zf<pv):
                pt.remove(p2)
                pt.remove(p3)
                i -= 2
            else:
                i += 1
        # 由于是成对删除的，应该不会出现以下这两种情况
        elif (p1[1] > p0[1] and p2[1] > p1[1]):  # 3点“丿”形上升中继
            pt.remove(p1)
            i -= 1
        elif (p1[1] > p0[1] and p2[1] > p1[1]):  # 3点“L”形下降中继
            pt.remove(p1)
            i -= 1
        else:
            i += 1

    pt = list(set([start] + pt + [end]))  # 去重
    pt.sort(key=lambda x: x[0])

    pout = []
    tout = []

    p1 = pt[0]
    for i in range(1, len(pt)):
        p2 = pt[i]
        if p2[1] > p1[1]:
            tout.append(p1)
            fg = 0
        else:
            pout.append(p1)
            fg = 1
        p1 = p2
    if fg == 0:
        pout.append(p2)
    else:
        tout.append(p2)

    pout = pd.DataFrame(pout, columns=['date', 'price'])
    pout = pout.set_index('date')
    pout = pout['price']

    tout = pd.DataFrame(tout, columns=['date', 'price'])
    tout = tout.set_index('date')
    tout = tout['price']

    return pout, tout

def peaks_troughs(peaks, troughs, pv, tv):
    '''
    pv:有效涨幅阈值，如0.2表示上涨幅度超过20%
    tv:有效回撤阈值，如0.2表示回撤幅度大于20%
    '''
#    pv=0.2
#    tv=0.2

    pt = []
    for i in peaks.index:
        pt.append((i, peaks[i]))
    for i in troughs.index:
        pt.append((i, troughs[i]))
    pt.sort(key=lambda x: x[0])

    start = pt[0]
    end = pt[-1]

    # 去掉上升中继和下跌中继
    i = 1
    while i < len(pt) - 1 and len(pt) > 3:

        if i < 1:
            i = 1
        p0 = pt[i-1]
        p1 = pt[i]
        p2 = pt[i+1]

        if (p1[1] > p0[1]) and (p2[1] < p1[1]):
            # 3点^形
            zf1 = abs(p1[1] / p0[1] - 1)     # 上涨幅度
            zf2 = abs(p2[1] / p1[1] - 1)     # 回调幅度            
            # 上涨、回调幅度都小于设定阈值，则删除该点，指针回调2
            # 回调幅度大于等于于设定阈值，指针前进1
            if (zf1 < tv) & (zf2 < pv):
                pt.remove(p1)
                pt.remove(p2)
                i -= 2
            else:
                i += 1
        elif ((p1[1] > p0[1]) and (p2[1] < p1[1])
                and (p3[1] > p2[1]) and (p2[1] >= p0[1])
                and (p3[1] <= p1[1])):
            # 4点N形上升通道情形二:下两点后点高于或等于前点，上两点后点低于或等于前点
            zf = abs(p2[1]/p1[1]-1)     # 回调幅度
            # 回调幅度小于设定阈值，则删除后面两点，指针回调2
            # 回调幅度大于等于于设定阈值，指针前进1
            if (zf<tv):
                pt.remove(p2)
                pt.remove(p3)
                i -= 2
            else:
                i += 1
        elif ((p1[1] < p0[1]) and (p2[1] > p1[1])
                and (p3[1] < p2[1]) and (p2[1] <= p0[1])
                and (p3[1] < p1[1])):
            # 4点倒N(VI)形下降通道情形一:上两点后点低于或等于前点，下两点后点低于于前点
            zf = abs(p2[1] / p1[1] - 1)     # 上升幅度
            # 上涨幅度小于设定阈值，则删除中间两点，指针回调2
            # 上涨幅度大于等于于设定阈值，指针前进1
            if (zf < pv):
                pt.remove(p1)
                pt.remove(p2)
                i -= 2
            else:
                i += 1
        elif ((p1[1] < p0[1]) and (p2[1] > p1[1])
                and (p3[1] < p2[1]) and (p2[1] <= p0[1])
                and (p3[1] >= p1[1])):
            # 4点倒N(VI)形下降通道情形二:上两点后点低于或等于前点，下两点后点高于或等于于前点
            zf = abs(p2[1] / p1[1] - 1)     #上涨幅度
            # 上涨幅度小于设定阈值，则删除后面两点，指针回调2
            # 上涨幅度大于等于于设定阈值，指针前进1
            if (zf<pv):
                pt.remove(p2)
                pt.remove(p3)
                i -= 2
            else:
                i += 1
        # 由于是成对删除的，应该不会出现以下这两种情况
        elif (p1[1] > p0[1] and p2[1] > p1[1]):  # 3点“丿”形上升中继
            pt.remove(p1)
            i -= 1
        elif (p1[1] > p0[1] and p2[1] > p1[1]):  # 3点“L”形下降中继
            pt.remove(p1)
            i -= 1
        else:
            i += 1

    pt = list(set([start] + pt + [end]))  # 去重
    pt.sort(key=lambda x: x[0])

    pout = []
    tout = []

    p1 = pt[0]
    for i in range(1, len(pt)):
        p2 = pt[i]
        if p2[1] > p1[1]:
            tout.append(p1)
            fg = 0
        else:
            pout.append(p1)
            fg = 1
        p1 = p2
    if fg == 0:
        pout.append(p2)
    else:
        tout.append(p2)

    pout = pd.DataFrame(pout, columns=['date', 'price'])
    pout = pout.set_index('date')
    pout = pout['price']

    tout = pd.DataFrame(tout, columns=['date', 'price'])
    tout = tout.set_index('date')
    tout = tout['price']

    return pout, tout

def max_up(peaks, troughs):
    '''
    查找最大涨幅
    '''
    tt = pp = zf = None

    for t in troughs.index:
        for p in peaks.index:
            if p > t:
                z = (peaks[p] / troughs[t] - 1) * 100
                if (zf is None) or zf < z:
                    zf = z
                    tt = t
                    pp = p

    return tt.strftime('%Y-%m-%d'), pp.strftime('%Y-%m-%d'), round(zf, 2)


if __name__ == "__main__":

    gpdm = '002451'
    tdxday = Tdxday(gpdm)
    start = '20180101'
    end = '20191231'
    df = tdxday.get_qfqdata(start=start, end=end)
    ds = round(df['close'], 4)
    sys.exit()
    # 波峰：大于前一，同时大于后一或等于后一且大于后二
    p = (ds.diff(1) > 0) & ((ds.diff(-1) > 0) | ((ds.diff(-1) == 0) & (ds.diff(-2) > 0)))
    peaks = ds.loc[p]
    # 波谷：小于前一，同时小于后一或等于后一且小于后二
    t = (ds.diff(1) < 0) & ((ds.diff(-1) < 0) | ((ds.diff(-1) == 0) & (ds.diff(-2) < 0)))
    troughs = ds.loc[t]
    # 起始点
    start = pd.Series([ds[0]], index=[ds.index[0]])
    end = pd.Series([ds[-1]], index=[ds.index[-1]])
    # 最先是波峰,则将起点加入波谷
    if peaks.index[0] < troughs.index[0]:  # 最先是峰,将起点加入谷
        troughs = start.append(troughs)
    else:
        peaks = start.append(peaks)
    # 最后是波峰,则将终点加入波谷
    if peaks.index[-1] > troughs.index[-1]:
        troughs = troughs.append(end)
    else:
        peaks = peaks.append(end)


    fig = plt.figure(figsize=(50, 10))
    plt.plot(ds)

#    peaks, troughs = best_peaks_troughs(peaks, troughs, 0.15, 0.20)

    print(max_up(peaks, troughs))

    for x in peaks.index:
        y = peaks[x]
        plt.text(x, y, y, fontsize=10, verticalalignment="bottom", horizontalalignment="center")
    for x in troughs.index:
        y = troughs[x]
        plt.text(x, y, y, fontsize=10, verticalalignment="top", horizontalalignment="center")

    plt.savefig('tmp1.png')
    plt.show()
    
    pv = 0.2
    tv = -0.15
    i = 0
    datas = []
    plst = [(idx, peaks[idx]) for idx in peaks.index]
    tlst = [(idx, troughs[idx]) for idx in troughs.index]
    for j in range(len(tlst)):
        row = []
        for k in range(len(plst)):
            if plst[k][0] > tlst[j][0]:  # 计算与后面波峰的涨幅
                zf = plst[k][1] / tlst[j][1] - 1
                zfbj = zf if zf > pv else 0
            else:  # 计算与前面波峰的跌幅
                zf = tlst[j][1] / plst[k][1] - 1
                zfbj = zf if zf < tv else 0
            row.append(zfbj)
        datas.append(row)

    df = pd.DataFrame(datas)
    df = df.replace(0, np.NaN)
    df.to_csv('pt3.csv')
    
    sys.exit()
    

    while True:
        if tlst[0][0] < plst[0][0]:  # 波谷在前
                    
            for j in range(len(tlst)):
                pp = None
                for k in range(len(plst)):
                    if plst[k][0] > tlst[j][0]:  # 计算与后面波峰的涨幅
                        zf = plst[k][1] / tlst[j] -1
                        if zf > pv:  # 涨幅超过指定阈值
                            pp = k  # 记录
                            break  #  退出循环
                        else:
                            pass  # 未超出阈值，循环继续
                    else:
                        pass  # 不计算与前面的波峰
                if pp == None:  # 波峰循环结束均没有超出阈值的波峰
                    pass
                else:  # 找到第一个超出阈值的波峰，将波峰、波谷从该位置切成两段
                    p1 = plst[:]
                    
        else:
            当前位置为波峰