# -*- coding: utf-8 -*-
"""
Created on 2019-10-06 20:30:01

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta


filename = '600138'
tdxday = Tdxday(filename)
df = tdxday.get_qfqdata('20150101')
rng_date = df.index

df = df.reset_index()  #重新按行号建立索引


def tick_category(frequency, step):
    '''
    刻度分类：根据频率和频数获取刻度的时间轴
    frequency 可取值: 'year','month','day','hour','minute','second'
    '''

    if frequency=='year':
        df['frequency'] = rng_date.strftime('%Y')
    elif frequency=='month':
        df['frequency'] = rng_date.strftime('%Y-%m')
    elif frequency=='day':
        df['frequency'] = rng_date.strftime('%Y-%m-%d')
    elif frequency=='hour':
        df['frequency'] = rng_date.strftime('%Y-%m-%d %H')
    elif frequency=='minute':
        df['frequency'] = rng_date.strftime('%Y-%m-%d %H:%M')
    elif frequency=='second':
        df['frequency'] = rng_date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        df['frequency'] = rng_date.strftime('%Y')

#    num_date = OrderedDict()
#    for item in df.groupby('frequency'):
#        num_date[item[1].index[-1]] = item[0]


    num_date = OrderedDict()
    for grp_id,grp_df in df.groupby('frequency'):
        num_date[grp_df.index[0]] = grp_id
        

    # 假定frequency=='year'
    #    for grp_id,grp_df in df.groupby('frequency'):
    #        print(grp_id)
    #        print("---")
    #        print(grp_df)

    #num_date内容如下：
    #OrderedDict([(243, '2015'),
    #             (487, '2016'),
    #             (721, '2017'),
    #             (964, '2018'),
    #             (1147, '2019')])
    
    #list切片list[n:m：s]，s步长 隔多少个元素取一次
    nums = list(num_date.keys())[::step]
    dates = list(num_date.values())[::step]
    return num_date,nums,dates

def show_plot(frequency, step, columns, tick_count=10):
    num_date,nums,dates = tick_category(frequency, step) 
    #nums:[243, 487, 721, 964, 1147]
    #dates:['2015', '2016', '2017', '2018', '2019']
    
    end_pos = nums[tick_count] if tick_count<len(nums) else nums[-1]
    data = df.loc[:,columns][:end_pos]
    axes = data.plot()
    axes.set_xticks(nums[:end_pos])
    axes.set_xticklabels(dates[:end_pos],rotation=45)
    plt.show()

show_plot('year',1, ['open', 'high','low','close'], tick_count=20)

show_plot('month',3, ['open', 'high','low','close'], tick_count=30)
