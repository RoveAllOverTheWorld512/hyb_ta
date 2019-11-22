# -*- coding: utf-8 -*-
"""
Created on 2019-11-08 10:20:53

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""


from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import *
import datetime
import time
import sys
import pandas as pd
import stock_pandas.tdx.tdxcfg as tdxcfg
import configparser

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

if __name__ == '__main__':
    now0 = datetime.datetime.now()

    td = datetime.datetime.today().strftime('%Y%m%d')
    tdx = tdxcfg.Tdx()
    gpdmb = tdx.get_gpdm()
    gpsssj = tdx.get_ssdate()
    gpdmb = gpdmb.join(gpsssj)
    #    gpdmb = gpdmb.loc[(gpdmb['ssdate'] <= td)]
    
    cols = ['market', 'code', 'active1', 'price', 'last_close',
            'open', 'high', 'low',
            'servertime', 'vol', 'cur_vol', 'amount', 's_vol', 'b_vol', ]
    
    api = TdxHq_API()
#    ip_port = bestip()
#    ip_port = {'ip': '218.6.198.174', 'port': 7709, 'name': '电信XX3'}
#    ip_port = {'ip': '101.207.135.103', 'port': 7709, 'name': '联通ES5'}
#    ip_port = {'ip': '182.131.7.211', 'port': 7709, 'name': '电信ES5'}
#    ip_port = {'ip': '182.131.7.212', 'port': 7709, 'name': '电信ES6'}
    ip_port = {'ip': '182.131.7.196', 'port': 7709, 'name': '电信ES1'}
    print(ip_port)
#    now0 = datetime.datetime.now()
    
    if api.connect(ip_port['ip'], ip_port['port']):
        all_stocks = []
        bad_stocks = []
        datas = []
        i = 0
        for idx, row in gpdmb.iterrows():
            all_stocks.append((0 if row.sc == 'sz' else 1, row.dm))
            if ((i + 1) % 50) == 0:
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