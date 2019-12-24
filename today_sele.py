# -*- coding: utf-8 -*-
"""
Created on 2019-10-11 09:12:38

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.class_func import *
from stock_pandas.tdx.tdxconstants import *
from stock_pandas.misc.supershort import *
from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter
import sys
import os
import datetime
import time
import pickle


def selefirstsignal(df):
    '''
    删除与前一个信号小于3周的重复信号
    '''
#    df = df.sort_index()
    if df.index.name == 'date' and ('date' not in df.columns):
        df = df.reset_index()
    df = df.sort_values(by=['gpdm', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.assign(tmp=df['date']-df['date'].shift(1))
    df.loc[df['gpdm'] != df['gpdm'].shift(1), 'tmp'] = None
    df = df.loc[((df['tmp'] > pd.Timedelta('21 days')) | pd.isnull(df['tmp']))]
    df = df.drop(columns=['tmp'])
    return df


if __name__ == '__main__':
    # 文件路径
#    path = os.path.dirname(os.path.realpath(__file__))
    path = DATA_PATH
    tdx = Tdx()
    gpdmb = tdx.get_gpdm()
    tsgp = gpdmb.loc[gpdmb['gpmc'].str.contains('退')]  # 退市股票名单
    df = None
    start = '2017-01-01'
    end = lastopenday()
#    end = '2019-12-22'
    end1 = end.replace('-', '')
#    end1 = datetime.datetime.now().strftime('%Y%m%d')
    gplblst = {'SHZBA': '沪市主板A股',
               'SZZBA': '深市主板A股',
               'SZZXBA': '深市中小板A股',
               'SZCYBA': '深市创业板A股'}
#               'SHKCBA': '沪市科创板A股',
    for lb in gplblst:
        csvfn = f'{DATA_PATH}\{lb}_20180501_{end1}_144_55_21_0.5_-0.25.csv'
        if os.path.exists(csvfn):
            df1 = pd.read_csv(csvfn, encoding='GBK',  parse_dates=True, infer_datetime_format=True)
            df1 = df1.loc[(df1['date'] >= end)]
            df = pd.concat([df, df1])
            
#    sys.exit()
    df = df.loc[~(df['gpdm'].isin(tsgp.index.tolist()))]  # 去掉即将退市的股票
    if not df.empty:
        df = df.reset_index(drop=True)
        # 持久化保存
        fn = 'yesterday.pickle'
        dump_pickle(path, fn, df)
        # 21天内跌幅超过20%
        df1 = df.loc[(df['decreasing_21'] < -0.2)]
        df1 = df1.sort_values(by='decreasing_21')

        # 55天内跌幅超过30%
        df2 = df.loc[(df['decreasing_55'] < -0.3)]
        df2 = df2.sort_values(by='decreasing_55')

        # 30天内跌幅超过25%
        df3 = df.loc[(df['n1_days'] < 30) & (df['decreasing_55'] < -0.25)]
        df3 = df3.sort_values(by='decreasing_55')

        # 21天内跌幅超过30%
        df4 = df.loc[(df['decreasing_21'] < -0.3)]
        df4 = df4.sort_values(by='decreasing_21')

        # 55天涨幅超过50%，回调21天内跌幅超过30%
        df5 = df.loc[(df['decreasing_21'] < -0.3)]
        df5 = df5.loc[(df['increasing_55'] > 0.5)]
        df5 = df5.sort_values(by='decreasing_21')

        # 55天内跌幅超过40%
        df6 = df.loc[(df['decreasing_55'] < -0.4)]
        df6 = df6.sort_values(by='decreasing_55')

        # 55天内跌幅超过50%
        df7 = df.loc[(df['decreasing_55'] < -0.5)]
        df7 = df7.sort_values(by='decreasing_55')
        fn = os.path.join(path, 'xg.xlsx')
        writer = pd.ExcelWriter(fn, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='全部', index=False)
        df1.to_excel(writer, sheet_name='21日跌幅超20%', index=False)
        df2.to_excel(writer, sheet_name='55日跌幅超30%', index=False)
        df3.to_excel(writer, sheet_name='30日跌幅超25%', index=False)
        df4.to_excel(writer, sheet_name='21日跌幅超30%', index=False)
        df5.to_excel(writer, sheet_name='55日涨50%__21日跌30%', index=False)
        df6.to_excel(writer, sheet_name='55日跌40%', index=False)
        df7.to_excel(writer, sheet_name='55日跌50%', index=False)
        writer.close()

        bkdict = {}
        bkn = CustomerBlockWriter()
        blockname = '跌幅超20'
        block_type = 'DF20'
        pos = 3
        codelist = df1['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '跌幅超30_55'
        block_type = 'DF30_55'
        pos = 2
        codelist = df2['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '跌幅超25'
        block_type = 'DF25'
        pos = 4
        codelist = df3['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '跌幅超30_21'
        block_type = 'DF30_21'
        pos = 1
        codelist = df4['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '涨50跌30'
        block_type = 'Z50D30'
        pos = 5
        codelist = df5['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '跌幅超40_55'
        block_type = 'DF40'
        pos = 6
        codelist = df6['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        blockname = '跌幅超50_55'
        block_type = 'DF50'
        pos = 7
        codelist = df7['gpdm']
        rewrite = True
        bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
        bkdict[block_type] = codelist.tolist()

        fn = 'blk.pickle'
        dump_pickle(path, fn, bkdict)
        
#    df.to_csv(r'f:\data\tmp4.csv', encoding='GBK', index=False)
#    df = df.loc[(df['decreasing_34'] < -0.25)]
#    df = df.loc[(df['increasing_55'] > 0.50)]
#    df = selefirstsignal(df)

#    sys.exit()
#    
#    data = []
#    j = 30
#    k = 20
#    n = 20
#    m = 60
#    ln = len(df)
#    start_time = time.time()
#    for i, gpxx in df.iterrows():
#        print(i, ln, gpxx.gpdm, gpxx.gpmc, gpxx.date)
#        dm = gpxx.gpdm[:6]
#        gpmc = gpxx.gpmc
#        date = gpxx.date.strftime('%Y-%m-%d')
#        tdxday = Tdxday(dm)
#        ohlc = tdxday.get_qfqdata(start='20160101')
#        data.append([gpxx.gpdm, gpmc, date] + supershort(ohlc, date, j, k, n, m))
#
#        if ((i + 1) % 50 == 0) or (i >= ln - 1):
#            now_time = time.time()
#            t1 = now_time - start_time
#            # 每只股票秒数
#            p = t1 / (i - k + 1)
#            # 估计剩余时间
#            t1 = t1 / 60
#            t2 = (ln - i) * p / 60
#
#            print('------已用时%d分钟，估计还需要%d分钟' % (t1, t2))
#
#
#    rs = pd.DataFrame(data,
#                      columns=['gpdm', 'gpmc', 'date',
#                               'date_max', 'days_max', 'close_max', 'zf_max',
#                               'date_1', 'close_1',
#                               'date_min', 'days_min', 'close_min', 'zf_min', 'zf_min_max', 
#                               'date1_max', 'days1_max', 'close1_max', 'zf1_max',
#                               'date2_min', 'days2_min', 'close2_min', 'zf2_min',
#                               'date3_max', 'days3_max', 'close3_max', 'zf3_max'])
#    rs = rs.round(4)
##    rs.to_csv(f'doublebottom_{j}_{k}_{n}.csv', encoding='GBK')
#    rs.to_csv(f'f:\data\supershort1_{start}_{end}_{j}_{k}_{n}.csv', encoding='GBK')
