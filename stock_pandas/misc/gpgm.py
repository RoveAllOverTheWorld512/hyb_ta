# -*- coding: utf-8 -*-
"""
Created on 2019-06-10 09:21:14

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

股票改名时间

"""

import sys
import os
import re
import pandas as pd
import xlrd
import sqlite3
from pypinyin import lazy_pinyin, Style, load_single_dict
import dateutil


def py(s):
    '''
    汉字拼音大写首字母缩写
    '''
    load_single_dict({ord('长'): 'cháng,zhǎng'})  # 调整 "长" 字的拼音顺序
    return ''.join(lazy_pinyin(s, style=Style.FIRST_LETTER))


def get_sylxls(file):
    '''
    从市盈率表提取个股数据
    '''
    print(file)
    rq = re.findall('csi(\d{8})\.xls', file)[0]
    try:
        wb = xlrd.open_workbook(file, encoding_override="cp1252")
    except:
        return None
    table = wb.sheet_by_name("个股数据")
    nrows = table.nrows  # 行数
    data = []

    row = table.row_values(0)  # 列名
    cols = [py(e) for e in row]  # 将列名转换成汉字拼音首字母
    data = [table.row_values(i) for i in range(1, nrows)]
    df = pd.DataFrame(data, columns=cols)
    df['zqdm'] = df['zqdm'].map(lambda x: x+('.SH' if x[0] == '6' else '.SZ'))
    df = df.replace('-', None)
    cols = 'gpdm,gpmc,hydm1,hymc1,hydm2,hymc2,hydm3,hymc3,hydm4,hymc4,\
    pe_lyr,pe_ttm,pb,gxl'.split(',')
    df.columns = cols  # 更改列名
    df['date'] = rq  # 添加日期
    return df


def get_gpmc(file):
    '''
    提取每日股票名称
    '''
    df = get_sylxls(file)
    cols = ['date', 'gpdm', 'gpmc']
    df = df[cols]  # 只提取三列
    return df


def get_fn(year=None, month=None, last=None):
    '''
    获取市盈率文件名
    '''
    pedir = r'd:\syl'
    files = os.listdir(pedir)
    df = pd.DataFrame(files, columns=['fn'])
    df = df.loc[df['fn'].str.match('csi\d{8}\.xls')]  # 去掉不是收益率的
    df['year'] = df['fn'].map(lambda x: x[3:7])
    df['month'] = df['fn'].map(lambda x: x[7:9])
    df['date'] = df['fn'].map(lambda x: x[3:11])
    df = df.sort_values(by=['date'])  # 排序
    if year is not None:
        year = str(year) if isinstance(year, int) else year
        if month is not None:
            month = str(month) if isinstance(month, int) else month
            if len(month) == 1:
                month = '0' + month
            df = df.loc[(df['year'] == year) & (df['month'] == month)]
        else:
            df = df.loc[(df['year'] == year)]
    if last is not None:
        df = df.loc[(df['date'] > last)]
    return df['fn'].to_list()


def get_gpmc_fromdb(gpdm):
    dbfn = r'f:\data\STOCKBASE.db'
    dbcn = sqlite3.connect(dbfn)
    curs = dbcn.cursor()
    curs.execute('select rq,gpmc from gpgm where gpdm=?', (gpdm, ))
    data = curs.fetchall()
    cols = ['date', 'gpmc']
    df = pd.DataFrame(data, columns=cols)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df
    
if __name__ == '__main__':
#    gpdm='600734.SH'
#    gpmc=get_gpmc_fromdb(gpdm)
#    sys.exit()
    dbfn = r'f:\data\STOCKBASE.db'
    dbcn = sqlite3.connect(dbfn)
    curs = dbcn.cursor()
    curs.execute('select rq,gpdm,gpmc from gpgm')
    data = curs.fetchall()
    cols = ['date', 'gpdm', 'gpmc']
    df = pd.DataFrame(data, columns=cols)
    # 按股票代码，日期，逆序排列，提取最新名称
    df = df.sort_values(by=['gpdm', 'date'], ascending=False)
    df1 = df.drop_duplicates(subset=['gpdm', 'gpmc'], keep='first')
    # 提取最后日期
    df1 = df1.sort_values(by='date', ascending=False)
    lastdate = df1.iloc[0].date
    # 最后日期原来的文件名
    files = get_fn(last=lastdate)
    # 提取股票名称
    df2 = pd.concat([get_gpmc(os.path.join(r'd:\syl', fn)) for fn in files])
    # 下面这条很关键，让从库中提取的最新名称重复导入，以便后面删除保留新加的股票名称
    df3 = pd.concat([df1, df1, df2])
    df4 = df3.drop_duplicates(subset=['gpdm', 'gpmc'], keep=False)
#    df = df.sort_values(by=['gpdm', 'date'])  # 按股票、日期排序
#    df = df.loc[(df['gpmc'] != df['gpmc'].shift(1))]  # 保留前后不一致的，即改名的
    data = df4.values.tolist()
    dbcn.executemany('INSERT OR IGNORE INTO GPGM (RQ,GPDM,GPMC) VALUES (?,?,?)', data)
    dbcn.commit()
    dbcn.close()

#    sys.exit()
#    
#    for year in range(2017, 2018):
#        files = get_fn(year)
#        df = pd.concat([get_gpmc(os.path.join(r'd:\syl', fn)) for fn in files])
#        df = df.sort_values(by=['date'])
#        df1 = df.drop_duplicates(subset=['gpdm', 'gpmc'], keep='first')
#        df1.to_csv(f'gn{year}.csv', index=False, encoding='GBK')
#        df1 = df1.loc[df1['gpmc'].str.contains('ST')]
#        df1.to_csv(f'st{year}.csv', index=False, encoding='GBK')
#
#    df = pd.concat([pd.read_csv(f'gn{year}.csv', parse_dates=True, infer_datetime_format=True,
#                   encoding='GBK') for year in range(2013,2020)])
#    df = df.sort_values(by=['gpdm', 'date'])  # 按股票、日期排序
#    df = df.loc[(df['gpmc'] != df['gpmc'].shift(1))]  # 保留前后不一致的，即改名的
#
#    df1 = df.loc[df['gpmc'].str.contains('ST') &
#                 df['date'].map(lambda x: str(x)).str.contains('2018')]  # 2019年改名为ST
#    df1 = df1.loc[~df1['gpmc'].str.contains('\*')]  # 去掉改名为*ST
##    df1.to_csv('tmp.csv', index=False, encoding='GBK')
#
#    df2 = df.loc[df['gpdm'].isin(df1['gpdm'].to_list())]
#    # 2019年改名为ST的股票的全部改名过程，包含2018年末未ST的股票
#
#    df3 = pd.concat([df2.loc[(df2['gpdm'] == r.gpdm) & (df2['date'] < r.date)]
#                    for i, r in df1.iterrows()])  # 提取改名ST之前的名称
#    df3 = df3.sort_values(by=['gpdm','date'])  # 按股票、日期升序排列
##    df3.to_csv('2019st2.csv', index=False, encoding='GBK')
#    df3 = df3.drop_duplicates(subset=['gpdm'], keep='last')  # 保留改名为ST之前最后的名称
#    df3 = df3.loc[~df3['gpmc'].str.contains('\*')] # 去掉改名为*ST
#    df3 = df3.loc[~df3['gpmc'].str.contains('ST')] # 去掉改名为ST，由于前面是按年份分析的名称
##    df3.to_csv('2019st1.csv', index=False, encoding='GBK')
#    df4 = df1.loc[df1['gpdm'].isin(df3['gpdm'].to_list())]  # 选取正常被ST，而非*ST变ST的
#    df4.to_csv('2018st2.csv', index=False, encoding='GBK')
