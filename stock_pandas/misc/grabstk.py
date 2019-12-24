# -*- coding: utf-8 -*-
"""
Created on 2019-12-18 10:24:59

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import sys
import os
import datetime
import win32clipboard as wc
import win32con
import chardet
import sqlite3
import pandas as pd
from stock_pandas.tdx.class_func import *
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.tdxconstants import *
from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter
from pyquery import PyQuery as pq


def getCopyText():
    '''
    提取windows系统剪贴板文本
    '''
    try:
        wc.OpenClipboard()
        copy_text = wc.GetClipboardData(win32con.CF_TEXT)
        wc.CloseClipboard()
        encode = chardet.detect(copy_text)  # 找到包含中文内容的字符串编码
        copy_text = copy_text.decode(encode['encoding'], errors='ignore')
    except:
        copy_text = ''
    return copy_text


def stkdict():
    '''
    生成抓取字典
    '''
    dbfn = os.path.join(SQLITE_PATH, 'STOCKBASE.db')
    dbcn = sqlite3.connect(dbfn)
    curs = dbcn.cursor()
    curs.execute('select gpdm,gpmc from gpgm')
    data = curs.fetchall()
    dbcn.close()
    cols = ['gpdm', 'gpmc']
    df = pd.DataFrame(data, columns=cols)
    df['dm'] = df['gpdm'].map(lambda x: x[:6])
    stkd = {}
    for i, row in df.iterrows():
        stkd[row['gpmc']] = row['gpdm']
        stkd[row['gpmc'].replace(' ', '')] = row['gpdm']
        if row['gpmc'].endswith('A'):
            stkd[row['gpmc'][:-1]] = row['gpdm']
        stkd[row['dm']] = row['gpdm']

    return stkd


def grab(txt, dic):
    '''
    按字典dic抓取文本txt中的股票代码
    '''
    try:
        stks = load_pickle(path, fn)
    except:
        stks = []

    for i in range(len(txt)):
        for j in range(2, 7):
            s = txt[i: i + j]
            if s in dic.keys():
                if dic[s] not in stks:
                    stks.append(dic[s])
    stks = list_drop(stks)
    dump_pickle(path, fn, stks)
    return stks


def get_cls_telegraph():
    '''
    从财联社电报网页提取
    '''
    url = 'https://www.cls.cn/telegraph'
    html = pq(url, encoding="utf-8")
    txts = html('span.jsx-29936494')
    # 持久化保存
    try:
        stks = load_pickle(path, fn)
    except:
        stks = []

    for i in range(len(txts)):
        txt = txts.eq(i).text()
        stk = grab(txt, dic)
#        print(txt)
        if len(stk):
            stks = list_add(stks, stk)

    stks = list_drop(stks)
    dump_pickle(path, fn, stks)
    return stks


def write_tmpblk(codelist):
    bkn = CustomerBlockWriter()
    blockname = '财联社'
    block_type = 'CLS'
    pos = 11
    rewrite = True
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)

if __name__ == '__main__':
#    tdx = Tdx()
#    gpdmb = tdx.get_gpdm()
    now1 = datetime.datetime.now().strftime('%H%M')

    global dic, path, fn, stks
    dic = stkdict()
    path = DATA_PATH
    fn = 'codelist.pickle'
    # 清空:下午16:00前清空就数据
    fn = os.path.join(path, fn)
    if os.path.exists(fn) :
        mtime = os.path.getmtime(fn)
        ltime = time.strftime("%Y%m%d%H%M", time.localtime(mtime))
        ltime1 = time.strftime("%Y%m%d", time.localtime(mtime))
        lstd = lastopenday().replace('-', '') + '2359'
        if (ltime < lstd) and (now1 < '1600'):
            os.rename(fn, f'{fn}.{ltime1}')  # 改名
            dump_pickle(path, fn, [])  # 清空

    stks = grab(getCopyText(), dic)
    stks = get_cls_telegraph()
    stks1 = sorted(stks, key=stks.index, reverse=True)  # 逆序，将新增的排在前面
    write_tmpblk(stks1)
    dump_pickle(path, fn, stks)
    print(len(stks))
