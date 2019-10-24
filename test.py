# -*- coding: utf-8 -*-
"""
Created on 2019-09-29 09:17:25

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta

if __name__ == '__main__':
    filename = '600138'
    tdxday = Tdxday(filename)
    df2 = tdxday.get_qfqdata(start='20190101')
    df2.ta.bottomreversal(append=True)

#    df2.to_csv('tmp1.csv')
#    df2.ta.alligator(append=True)
#    df2 = df2.assign(bias = 100 * (df2['close'] - df2['ALLIGATOR_TEETH_8_5']) / df2['ALLIGATOR_TEETH_8_5'])
#    df2.ta.fractals(append=True)    
#    df2=df2.assign(A=(df2['bias']>15),B=(df2['bias']<-15))
    
#if __name__ == '__main__':
#    tdxday = Tdxday(r'D:\tdx\sz002294.day')
#    df = tdxday.get_data()
#
#    df2 = get_data(r'D:\tdx\szlday\sz002294.day')
#
#    df3 = get_data(r'D:\tdx\sz002294.day')
#
#    tdx = Tdx()
#    gnbk = tdx.get_tdxblk()
#    gnbk = tdx.get_tdxblk('fg')
#    gnbk = tdx.get_tdxblk('zs')
#
#    
#    gpdmb = tdx.get_gpdm()
#    
#    ssrq = tdx.get_ssdate()
#    print(__file__)

#if __name__ == '__main__':
#    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#print('#########################')
#
#print(__file__)
#print(os.path.realpath(__file__))
#print(os.path.dirname(os.path.realpath(__file__)))
#print('#########################')
#pprint.pprint(sys.path)

#high = df['high']
#low = df['low']
#
#alligatordf = ta.alligator(high, low, long=13, mid=8, short=5, long_offset=8, \
#              mid_offset=5, short_offset=3)
#    
#df = pd.read_csv(r'F:\pandas_hybta\data\600674.csv', index_col='date',
#                 parse_dates=True)
#
##df.ta.ao(append=True)
#df.ta.fractals(append=True)
#df.ta.alligator(append=True)

#



#def up_fractal(high):
#    h_df = high.to_frame()
#    #与前一天比较，高于前一天为1
#    h_1 = (high.diff(1) > 0).astype(int)
#    #与前第二天比较，高于前第二天为1
#    h_2 = (high.diff(2) > 0).astype(int)
#    #同时高于前两天为1
#    h_12 = ((h_1 + h_2) == 2).astype(int)
#    #与后一天比较，高于于后一天为1
#    h1 = (high.diff(-1) > 0).astype(int)
#    #与后第二天比较，高于于后第二天为1    
#    h2 = (high.diff(-2) > 0).astype(int)
#    #同时高于后两天为1
#    h12 = ((h1 + h2) == 2).astype(int)
#    #合并数据
#    h_df['h_12'] = h_12
#    h_df['h12'] = h12
#    #连续上涨的只记录最后一个高点
#    i = 0
#    while i < len(h_df) - 1:
#        if (h_df.iloc[i + 1, 1] == 1):
#            h_df.iloc[i, 1] = 0    
#        i += 1
#    #间隔一天继续上涨的去掉间隔前一天高点
#    i = 0
#    while i < len(h_df) - 2:
#        if (h_df.iloc[i + 2, 1] == 1):
#            h_df.iloc[i, 1] = 0
#        i += 1
#    #逆序
#    h_df = h_df.sort_index(ascending=False)
#    #连续下跌只记录开始一天
#    i = 0
#    while i < len(h_df) - 1:
#        if (h_df.iloc[i + 1, 2] == 1):
#            h_df.iloc[i,2] = 0    
#        i += 1
#    #间隔一天继续下跌的去掉间隔前一天高点    
#    i = 0
#    while i<len(h_df) - 2:
#        if (h_df.iloc[i + 2, 2] == 1):
#            h_df.iloc[i, 2] = 0  
#        i += 1
#    #正序
#    h_df = h_df.sort_index()
#    #去掉中继高点    
#    i = 0
#    bg = False
#    ii = 0
#    while i < len(h_df):
#        if (h_df.iloc[i, 1] == 1):
#            if bg:
#                h_df.iloc[ii, 1] = 0
#            if (h_df.iloc[i, 2] == 1):
#                bg = False
#            else:
#                bg = True
#                ii = i
#        else:
#            if (h_df.iloc[i, 2] == 1):
#                bg = False
#            else:
#                pass
#        i += 1
#    #返回结果
#    return h_df['h_12']
#
#def up_or_down(series,fractal_type=1):
#
#    hl_df = series.to_frame()
#
#    if fractal_type == 1:
#        #与前一天比较，高于前一天为1
#        hl_1 = (series.diff(1) > 0).astype(int)
#        #与前第二天比较，高于前第二天为1
#        hl_2 = (series.diff(2) > 0).astype(int)
#        #与后一天比较，高于后一天为1
#        hl1 = (series.diff(-1) > 0).astype(int)
#        #与后第二天比较，高于后第二天为1    
#        hl2 = (series.diff(-2) > 0).astype(int)
#    else:
#        #与前一天比较，低于前一天为1
#        hl_1 = (series.diff(1) < 0).astype(int)
#        #与前第二天比较，低于前第二天为1
#        hl_2 = (series.diff(2) < 0).astype(int)
#        #与后一天比较，低于后一天为1
#        hl1 = (series.diff(-1) < 0).astype(int)
#        #与后第二天比较，低于后第二天为1    
#        hl2 = (series.diff(-2) < 0).astype(int)
#
#    #同时高(低)于前两天为1
#    hl_12 = ((hl_1 + hl_2) == 2).astype(int)
#    #同时高(低)于后两天为1
#    hl12 = ((hl1 + hl2) == 2).astype(int)
#
#    #合并数据
#    hl_df['hl_12'] = hl_12
#    hl_df['hl12'] = hl12
#
#    #连续上涨（下跌）的只记录最后一个高(低)点
#    i = 0
#    while i < len(hl_df) - 1:
#        if (hl_df.iloc[i + 1, 1] == 1):
#            hl_df.iloc[i, 1] = 0    
#        i += 1
#
#    #间隔一天继续上涨（下跌）的去掉间隔前一天高（低）点
#    i = 0
#    while i < len(hl_df) - 2:
#        if (hl_df.iloc[i + 2, 1] == 1):
#            hl_df.iloc[i, 1] = 0
#        i += 1
#
#    #逆序
#    hl_df = hl_df.sort_index(ascending=False)
#
#    #连续下跌（上涨）只记录开始一天
#    i = 0
#    while i < len(hl_df) - 1:
#        if (hl_df.iloc[i + 1, 2] == 1):
#            hl_df.iloc[i,2] = 0    
#        i += 1
#
#    #间隔一天继续下跌（上涨）的去掉间隔前一天高（低）点    
#    i = 0
#    while i<len(hl_df) - 2:
#        if (hl_df.iloc[i + 2, 2] == 1):
#            hl_df.iloc[i, 2] = 0  
#        i += 1
#
#    #正序
#    hl_df = hl_df.sort_index()
#
#    #去掉中继高（低）点    
#    i = 0
#    bg = False
#    ii = 0
#    while i < len(hl_df):
#        if (hl_df.iloc[i, 1] == 1):
#            if bg:
#                hl_df.iloc[ii, 1] = 0
#            if (hl_df.iloc[i, 2] == 1):
#                bg = False
#            else:
#                bg = True
#                ii = i
#        else:
#            if (hl_df.iloc[i, 2] == 1):
#                bg = False
#            else:
#                pass
#        i += 1
#
#    # 返回结果
#    return hl_df['hl_12']
#
#
#df = pd.read_csv(r'F:\pandas_hybta\data\600674.csv', index_col='date',
#                 parse_dates=True)
#high = df['high']
#
#up_fractals = up_or_down(high)
#
#low = df['low']
#down_fractals = up_or_down(low,2)
#
#df['up_fractal']=up_fractals
#df['down_fractal']=down_fractals
#
#df.to_csv('tmp1.csv')
