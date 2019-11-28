# -*- coding: utf-8 -*-
"""
Created on 2019-11-27 18:57:15

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import os
import pandas as pd
from stock_pandas.tdx.class_func import *
from stock_pandas.tdx.tdxconstants import *
from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter


def zxg():
    '''
    自选股
    zxgmore.dat结构分析:
    00-01：市场,短整数
    02-32：交易代码,字符串
    33-36：日期1,整数
    37-40：价格1,浮点数
    41-44：日期2,整数
    45-48：价格2，浮点数
    49-52：涨跌幅，浮点数
    53-56：证券代码，整数
    57-79：保留
    '''
#    fn = r'D:\new_hxzq_hc\T0002\blocknew\zxgmore.dat'
#    f = open(fn,'rb')
#    block_data = f.read()
#    pos = 0
#    n1 = block_data[pos: pos + 80]
#    n2 = n1[53:]
#    sc, gpdm, rq1, jg1, rq2, jg2, zf, dm = struct.unpack(_format, n1)
#    gpdm=gpdm.decode('gbk', 'ignore').rstrip("\x00")
#    

    _format = '<H31sififfi23x'
    fname = TDX_BLOCKNEW
    bf = '/'.join([fname, 'zxgmore.dat'])
    with open(bf, 'rb') as f:
        block_data = f.read()
        pos = 0
        result = []
        while pos < len(block_data):
            n1 = block_data[pos: pos + 80]
            sc, gpdm, rq1, jg1, rq2, jg2, zf, dm = struct.unpack(_format, n1)
            gpdm=gpdm.decode('gbk', 'ignore').rstrip("\x00")

            gpdm = n1[2:8]
            pos = pos + 80
            sc, fl = get_gpfl(gpdm)
            if sc is not None:
                code = '0' + gpdm + '\n' if gpdm[0] != '6' else '1' + gpdm + '\n'
                if (code not in lst):
                    result.append(code)

    return result


if __name__ == '__main__':

    fname = TDX_BLOCKNEW
    bkn = CustomerBlockWriter()
    strlst = '''000069,
000885,
001872,
002154,
002451,
002734,
002969,
300059,
300384,
600399,
600566,
600674'''.split(',\n')
    lst = bkn.gen_codelist(strlst)
#    zxglst = list(set(zxg()))
    
#    ret = [ i for i in zxglst if i not in lst ]
    bkn.write_blk('ZXG', lst + zxglst)
