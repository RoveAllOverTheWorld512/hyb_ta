# -*- coding: utf-8 -*-
"""
Created on 2019-11-27 18:57:15

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

使用Python模块：struct模块
https://blog.csdn.net/abc_12366/article/details/80211953


"""

import os
import struct
import pandas as pd
from stock_pandas.tdx.class_func import *
from stock_pandas.tdx.tdxconstants import *
from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter


def read_col_cfgwarn():
    '''
    自选股
    col_cfgwarn.dat结构分析:
    文件头：
    0000H--0363H:868个字节，结构不详，x
    0364H--0367H:4个字节，预警品种数量，I整数
    0368H--036BH:4个字节，保留，x
    预警条件：每条61字节
    00-05：6字节，交易代码,s字符串
    06-22：17字节，保留,x
    23-24：2字节，市场代码,H整数，0深市、1沪市
    25-28：4字节，上破价，f浮点
    29-32：4字节，下破价，f浮点
    33-33：1字节，上破价提示交易标记，B整数，0无、1闪电买入、2闪电卖出
    34-34：1字节，下破价提示交易标记，B整数，0无、1闪电买入、2闪电卖出
    35-35：1字节，分时线金叉死叉标记，B整数，0无、1启用
    36-36：1字节，不详，B整数
    37-38：2字节,ETF折溢率*100,H整数
    39-40：2字节,换手率*100,H整数
    41-42：2字节,涨幅*100,H整数
    43-44：2字节,涨速*100,H整数
    45-60：16字节，保留，x
    '''

    _format = '<HffBBBBHHHH16x'
    path = TDX_T0002
    fn = '/'.join([path, 'col_cfgwarn.dat'])
    with open(fn, 'rb') as f:
        block_data = f.read()
        block_head = block_data[0:876]
        block_data = block_data[876:]
        num, = struct.unpack('<868xI4x', block_head)
        pos = 0
        result = []
        while pos < len(block_data):
            n1 = block_data[pos: pos + 23]
            n2 = block_data[pos + 23: pos + 61]
            gpdm, = struct.unpack('<6s17x', n1)
            sc, spj, xpj, spcz, xpcz, jcsc, tmp, zyl, hsl, zf, zs = struct.unpack(_format, n2)
            gpdm=gpdm.decode('gbk', 'ignore').rstrip("\x00")

            pos = pos + 61
            spj = round(spj, 4)
            xpj = round(xpj, 4)
            hsl = hsl / 100
            zf = zf /100
            zs = zs /100
            dt = [gpdm, sc, spj, xpj, spcz, xpcz, jcsc, tmp, zyl, hsl, zf, zs]            
            result.append(dt)
        f.close()

    return num, result


if __name__ == '__main__':

    n, warnlst = read_col_cfgwarn()
    columns = 'gpdm,sc,spj,xpj,spcz,xpcz,jcsc,tmp,zyl,hsl,zf,zs'.split(',')
    df = pd.DataFrame(warnlst, columns=columns)
    df.to_csv(r'f:\data\tmp.csv')