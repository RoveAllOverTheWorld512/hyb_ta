# -*- coding: utf-8 -*-
"""
Created on 2019-10-07 11:58:23

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import sys
from matplotlib import pyplot as plt
from matplotlib.pylab import date2num, datestr2num
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.pylab import mpl

import tkinter as tk
import mpl_finance as mpf
import pandas as pd
import numpy as np
import datetime
import time

from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta


root = tk.Tk()
root.title("tkinter and matplotlib")


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

mpl.rcParams['font.sans-serif'] = ['SimHei']  #中文显示
mpl.rcParams['axes.unicode_minus']=False      #负号显示


##############################################################################
filename = '600138'
tdxday = Tdxday(filename)
stock = tdxday.get_qfqdata(start='20190101')

stock = stock.reset_index()
#stock['date'] = stock['date'].map(lambda x: x.strftime('%Y-%m-%d'))

stock['date_num'] = stock['date'].map(date2num)

stock = stock[['date_num', 'open', 'high', 'low', 'close','volume']]
quotes = stock.values.tolist()

#figsize定义图像大小，dpi定义像素
fig, ax = plt.subplots()

fig.subplots_adjust(bottom=0.1)
ax.xaxis_date()
plt.xticks(rotation=45) #日期显示的旋转角度
plt.title('002294')
plt.xlabel('time')
plt.ylabel('price')
mpf.candlestick_ohlc(ax,quotes,width=0.7,colorup='r',colordown='green') 
# 上涨为红色K线，下跌为绿色，K线宽度为0.7
plt.grid(True)

canvs = FigureCanvasTkAgg(fig, root)#f是定义的图像，root是tkinter中画布的定义位置
canvs.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
canvs.draw()

button = tk.Button(master=root, text="退出", command=_quit)
button.pack(side=tk.BOTTOM)


root.mainloop()
