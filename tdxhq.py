# -*- coding: utf-8 -*-
"""
Created on 2019-11-08 10:20:53

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import datetime
import time
import sys
import os
import pickle
import pandas as pd
import configparser
from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import *
from pytdx.reader.block_reader import *
import stock_pandas.tdx.tdxcfg as tdxcfg
from stock_pandas.tdx.class_func import *
from stock_pandas.tdx.tdxconstants import *
from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter


def bestip():
    cfg = configparser.ConfigParser()
    cfg.read(r'D:\new_hxzq_hc\connect1.cfg')
    hostnum = cfg.getint("HQHOST", 'hostnum')
    for i in range(hostnum):
        name = 'hostname' + str(i + 101)[1:]
        name = cfg.get('HQHOST', name)
        ip = 'IPAddress' + str(i + 101)[1:]
        ip = cfg.get('HQHOST', ip)
        port = 'Port' + str(i + 101)[1:]
        port = cfg.getint('HQHOST', port)
        stock_ip.append({'ip': ip, 'port': port, 'name': name})
    return select_best_ip('stock')


def get_customerblk(blktype):
    reader = CustomerBlockReader()
    blk = reader.get_df(TDX_BLOCKNEW,
                        BlockReader_TYPE_GROUP)

    blk = blk.loc[(blk['block_type'] == blktype)]
    dmlst = blk['code_list']
    return dmlst.tolist()


if __name__ == '__main__':
    # 文件路径
    now0 = datetime.datetime.now()
    path = DATA_PATH

    fn = 'yesterday.pickle'
    df1 = load_pickle(path, fn)
    df1 = df1.set_index('gpdm', drop=False)

    fn = 'blk.pickle'
    blk = load_pickle(path, fn)

    now1 = datetime.datetime.now()
    print(now1 - now0)
    now0 = datetime.datetime.now()

    td = datetime.datetime.today().strftime('%Y%m%d')
    tdx = tdxcfg.Tdx()
    gpdmb = tdx.get_gpdm()
    gpsssj = tdx.get_ssdate()
    gpdmb = gpdmb.join(gpsssj)
    dmb_df20 = get_customerblk('DF20')[0].split(',')
    dmb_df30_55 = get_customerblk('DF30_55')[0].split(',')
#    gpdmb = gpdmb.loc[gpdmb['dm'].isin(dmb)]
#    sys.exit()

    #    gpdmb = gpdmb.loc[(gpdmb['ssdate'] <= td)]

    cols = ['market', 'code', 'active1', 'price', 'last_close',
            'open', 'high', 'low',
            'servertime', 'vol', 'cur_vol', 'amount', 's_vol', 'b_vol', ]

    api = TdxHq_API()
#    ip_port = bestip()
#    ip_port = {'ip': '218.6.198.174', 'port': 7709, 'name': '电信XX3'}
    ip_port = {'ip': '101.207.135.103', 'port': 7709, 'name': '联通ES5'}
#    ip_port = {'ip': '182.131.7.211', 'port': 7709, 'name': '电信ES5'}
#    ip_port = {'ip': '182.131.7.212', 'port': 7709, 'name': '电信ES6'}
#    ip_port = {'ip': '182.131.7.196', 'port': 7709, 'name': '电信ES1'}
#    ip_port = {'ip': '120.86.124.75', 'port': 7709, 'name': '深证云联通NF'}
    print(ip_port)
#    now0 = datetime.datetime.now()

    if api.connect(ip_port['ip'], ip_port['port']):
        all_stocks = []
        bad_stocks = []
        datas = []
        i = 0
        for idx, row in gpdmb.iterrows():
            all_stocks.append((0 if row.sc == 'sz' else 1, row.dm))
#            print(i)
            if ((i + 1) % 50 == 0) or (i >= len(gpdmb) - 1):
                stocks = None
                stocks = api.get_security_quotes(all_stocks)
#                time.sleep(2)
#                print(f'i={i}')
                if stocks is not None:
#                    print(f'OK')
                    datas = datas + stocks
                else:
                    bad_stocks = bad_stocks + all_stocks
                all_stocks = []
            i += 1
        bad_stocks1 = []
        for all_stocks in bad_stocks:
#            print(all_stocks)
            stocks = api.get_security_quotes(all_stocks)
            if stocks is not None:
#                print(f'OK')
                datas = datas + stocks
            else:
                bad_stocks1.append(all_stocks)

        stocks = api.get_security_quotes(bad_stocks1)
        if stocks is not None:
            datas = datas + stocks

    #        pprint.pprint(stocks)
    if len(datas) != 0:
        stocksdf = pd.DataFrame(datas)
        stocksdf = stocksdf[cols]
        stocksdf['gpdm'] = ''
        stocksdf.loc[stocksdf['market'] == 1, 'gpdm'] = stocksdf['code'] + '.SH'
        stocksdf.loc[stocksdf['market'] == 0, 'gpdm'] = stocksdf['code'] + '.SZ'
        stocksdf = stocksdf.set_index('gpdm')
        stocksdf['gpmc'] = gpdmb['gpmc']
        stocksdf=stocksdf.assign(pct_chg=(stocksdf['price']/stocksdf['last_close']-1)*100)
        df = stocksdf[['gpmc', 'price', 'last_close', 'pct_chg', 'active1', 'servertime']]
    now1 = datetime.datetime.now()
    print(now1 - now0)

    df1 = df1.join(df, lsuffix='_1')
    df1 = df1.assign(desc_21=df1['price']/df1['max_21']-1)
    df1 = df1.assign(desc_55=df1['price']/df1['max_55']-1)
    df1.loc[df1['price'] == 0, 'desc_21'] = None
    df1.loc[df1['price'] == 0, 'desc_55'] = None
    df1.loc[df1['desc_21'] > 0, 'desc_21'] = None
    df1.loc[df1['desc_55'] > 0, 'desc_55'] = None

    df2 = df1.loc[df1['desc_21'] < -0.2]
    df2 = df2.sort_values(by='desc_21')
    df3 = df2.loc[df1['desc_21'] < -0.3]

    df5 = df1.loc[df1['desc_55'] < -0.3]
    df5 = df5.sort_values(by='desc_55')
    df6 = df5.loc[df1['desc_55'] < -0.4]
    df7 = df6.loc[df1['desc_55'] < -0.5]

    bkn = CustomerBlockWriter()
    blockname = '跌幅超20'
    block_type = 'DF20'
    pos = 3
    codelist = df2['gpdm']
    rewrite = True
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
#    print(list_sub(blk[block_type], codelist.tolist()))
    print(block_type)
    print(list_sub(codelist.tolist(), blk[block_type]))

#    sys.exit()

    blockname = '跌幅超30_55'
    block_type = 'DF30_55'
    pos = 2
    codelist = df6['gpdm']
    rewrite = True
    print(block_type)
#    print(list_sub(blk[block_type], codelist.tolist()))
    print(list_sub(codelist.tolist(), blk[block_type]))
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)

    blockname = '跌幅超40_55'
    block_type = 'DF40'
    pos = 6
    codelist = df6['gpdm']
    rewrite = True
    print(block_type)
#    print(list_sub(blk[block_type], codelist.tolist()))
    print(list_sub(codelist.tolist(), blk[block_type]))
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)

    blockname = '跌幅超50_55'
    block_type = 'DF50'
    pos = 7
    codelist = df7['gpdm']
    rewrite = True
    print(block_type)
#    print(list_sub(blk[block_type], codelist.tolist()))
    print(list_sub(codelist.tolist(), blk[block_type]))
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
    fn = os.path.join(path, 'tmp.csv')
    df1.to_csv(fn, encoding='GBK')
