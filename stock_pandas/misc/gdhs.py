# -*- coding: utf-8 -*-
"""
Created on 2019-11-13 21:58:53

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd
import sqlite3
import datetime
import sys
import os


def get_date():
    '''
    5月1日（120）前公布年报和一季报
    9月1日（243）前公布半年报
    11月1日（304）前公布三季报
    '''
    today = datetime.datetime.today()
    first = datetime.datetime(today.year, 1, 1)
    n = (today - first).days

    if n < 120:
        rq1 = f'{today.year-1}-09-30'
        rq2 = f'{today.year-2}-12-31'
        rq3 = f'{today.year-2}-09-30'
    elif n < 243:
        rq1 = f'{today.year}-03-31'
        rq2 = f'{today.year-1}-12-31'
        rq3 = f'{today.year-1}-03-31'
    elif n < 304:
        rq1 = f'{today.year}-06-30'
        rq2 = f'{today.year-1}-12-31'
        rq3 = f'{today.year-1}-06-30'
    else:
        rq1 = f'{today.year}-09-30'
        rq2 = f'{today.year-1}-12-31'
        rq3 = f'{today.year-1}-09-30'
    return rq1, rq2, rq3


def get_quarters(m=8):
    '''
    5月1日（120）前公布年报和一季报
    9月1日（243）前公布半年报
    11月1日（304）前公布三季报
    '''
    today = datetime.datetime.today()
    first = datetime.datetime(today.year, 1, 1)
    n = (today - first).days

    if n < 120:
        rq1 = datetime.datetime(today.year-1, 9, 30)
    elif n < 243:
        rq1 = datetime.datetime(today.year, 3, 31)
    elif n < 304:
        rq1 = datetime.datetime(today.year, 6, 30)
    else:
        rq1 = datetime.datetime(today.year, 9, 30)

    quarters = [rq1]
    for i in range(1, m):
        rq = datetime.datetime(rq1.year, rq1.month - 2, 1) - datetime.timedelta(days=1)
        quarters.append(rq)
        rq1 = rq
    return quarters


def get_gdhs_fromdb():
    '''
    # 获取最新股东户数及季度环比变化，股东户数从大智慧网抓取
    # 每天运行d:\selestock\dzh_gdhs2sqlite.py保存在d:\hyb\DZH.db
    '''
    dbfn = r'd:\hyb\DZH.db'
    dbcn = sqlite3.connect(dbfn)
    curs = dbcn.cursor()
    # rq0最新、rq1最新季度、rq2最新年度、rq3上一年度同期
    rq1, rq2, rq3 = get_date()
    # 提取年报以来最新股东户数，注意最新在前
    sql = "select gpdm,rq,gdhs from gdhs where rq>='%s' order by rq desc;" % rq2
    curs.execute(sql)
    data = curs.fetchall()
    # 保留最新户数
    df0 = pd.DataFrame(data, columns=['gpdm', 'rq0', 'gdhs0'])
    df0 = df0.drop_duplicates(['gpdm'], keep='first')
    df0 = df0.set_index('gpdm')

    sql = "select gpdm,rq,gdhs from gdhs where rq='%s' order by rq desc;" % rq1
    curs.execute(sql)
    data = curs.fetchall()
    df1 = pd.DataFrame(data, columns=['gpdm', 'rq1', 'gdhs1'])
    df1 = df1.set_index('gpdm')

    sql="select gpdm,rq,gdhs from gdhs where rq=='%s' order by rq desc;" % rq2
    curs.execute(sql)
    data = curs.fetchall()
    df2 = pd.DataFrame(data, columns=['gpdm', 'rq2', 'gdhs2'])
    df2 = df2.set_index('gpdm')

    sql = "select gpdm,rq,gdhs from gdhs where rq=='%s' order by rq desc;" % rq3
    curs.execute(sql)
    data = curs.fetchall()
    df3 = pd.DataFrame(data, columns=['gpdm', 'rq3', 'gdhs3'])
    df3 = df3.set_index('gpdm')

    dbcn.close()

    df = df0.join(df1)
    df = df.join(df2)
    df = df.join(df3)

    # 最新股东户数与最新季度户数比较
    df.eval('gdhsjb = (gdhs0 / gdhs1-1) * 100', inplace=True)
    # 最新季度户数与年初户数比较
    df.eval('gdhshb = (gdhs1 / gdhs2-1) * 100', inplace=True)
    # 最新季度户数与年初户数比较
    df.eval('gdhstb = (gdhs2 / gdhs3-1) * 100', inplace=True)
    df = df.loc[(df['rq0'] >= rq1)]
    return df.round(2)


def get_gdhs_fromdb1(m):
    '''
    # 获取最新股东户数及季度环比变化，股东户数从大智慧网抓取
    # 每天运行d:\selestock\dzh_gdhs2sqlite.py保存在d:\hyb\DZH.db
    '''
    rqs = get_quarters(m)
    dbfn = r'd:\hyb\DZH.db'
    dbcn = sqlite3.connect(dbfn)
    curs = dbcn.cursor()
    rq = rqs[0].strftime('%Y-%m-%d')
    sql = "select gpdm,rq,gdhs from gdhs where rq>='%s' order by rq desc;" % rq
    curs.execute(sql)
    data = curs.fetchall()
    # 保留最新户数
    df = pd.DataFrame(data, columns=['gpdm', 'rq0', 'gdhs0'])
    df = df.drop_duplicates(['gpdm'], keep='first')
    df = df.set_index('gpdm')
    i = 1
    for rq in rqs:
        rq=rq.strftime('%Y-%m-%d')
        sql = "select gpdm,rq,gdhs from gdhs where rq='%s';" % rq        
        curs.execute(sql)        
        data = curs.fetchall()
        cols = ['gpdm',f'rq{i}', f'gdhs{i}']        
        df1 = pd.DataFrame(data,columns=cols)
        df1 = df1.set_index('gpdm')
        df=df.join(df1)
        i += 1

    dbcn.close()    

    return df



if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname
                    (os.path.dirname
                     (os.path.dirname
                      (os.path.realpath
                       (__file__)))))

    from stock_pandas.tdx.class_func import *
    from stock_pandas.tdx.tdxcfg import Tdx
    from stock_pandas.tdx.tdxwriteblocknew import CustomerBlockWriter
    
    tdx = Tdx()
    gpdmb = tdx.get_gpdm()
    gpsssj = tdx.get_ssdate()
    gpsssj.index.name = gpsssj.index.name.lower()
    gdhs = get_gdhs_fromdb1(12)
    gdhs = pd.merge(gdhs, gpdmb, on='gpdm', how='left')
    gdhs = pd.merge(gdhs, gpsssj, on='gpdm', how='left')
    gdhs = dfsortcolumns(gdhs, subset='gpdm,gpmc,ssdate')
    gdhs = gdhs.drop(columns=['sc', 'dm', 'gppy', 'gplb'])
    gdhs = gdhs.assign(gdhsb=gdhs['gdhs0']/gdhs['gdhs12'])
    gdhs = gdhs.sort_values(by='gdhsb')
    fn = r'f:\data\gdhs.xlsx'
    writer=pd.ExcelWriter(fn, engine='xlsxwriter')
    df1 = gdhs.loc[(gdhs['gdhs0'] <= gdhs['gdhs1'])]
    df2 = df1.loc[(df1['gdhs1'] <= df1['gdhs2'])]
    df3 = df2.loc[(df2['gdhs2'] <= df2['gdhs3'])]
    df4 = df3.loc[(df3['gdhs3'] <= df3['gdhs4'])]
    df5 = df4.loc[(df4['gdhs4'] <= df4['gdhs5'])]
    df6 = df5.loc[(df5['gdhs5'] <= df5['gdhs6'])]
    df7 = df6.loc[(df6['gdhs6'] <= df6['gdhs7'])]
    df8 = df7.loc[(df7['gdhs7'] <= df7['gdhs8'])]
    df9 = df8.loc[(df8['gdhs8'] <= df8['gdhs9'])]
    df10 = df9.loc[(df9['gdhs9'] <= df9['gdhs10'])]
    df11 = df10.loc[(df10['gdhs10'] <= df10['gdhs11'])]
    df12 = df11.loc[(df11['gdhs11'] <= df11['gdhs12'])]
    gdhs.to_excel(writer, sheet_name='全部', index=False)
    df1.to_excel(writer, sheet_name='选股1', index=False)   
    df2.to_excel(writer, sheet_name='选股2', index=False)   
    df3.to_excel(writer, sheet_name='选股3', index=False)   
    df4.to_excel(writer, sheet_name='选股4', index=False)   
    df5.to_excel(writer, sheet_name='选股5', index=False)   
    df6.to_excel(writer, sheet_name='选股6', index=False)   
    df7.to_excel(writer, sheet_name='选股7', index=False)   
    df8.to_excel(writer, sheet_name='选股8', index=False)   
    df9.to_excel(writer, sheet_name='选股9', index=False)   
    df10.to_excel(writer, sheet_name='选股10', index=False)   
    df11.to_excel(writer, sheet_name='选股11', index=False)   
    df12.to_excel(writer, sheet_name='选股12', index=False)   
    writer.close()

    bkn = CustomerBlockWriter()
    rewrite = True
    blockname = '股东减1'
    block_type = 'GDJ1'
    pos = 3
    codelist = df4['gpdm']
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)

    blockname = '股东减2'
    block_type = 'GDJ2'
    pos = 4
    codelist = df6['gpdm']
    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)


#def dm():
#    fn = r'f:\data\gdhs.xlsx'
#    writer=pd.ExcelWriter(fn, engine='xlsxwriter')
##    gdhs.to_csv(r'f:\data\gdhs.csv', encoding='GBK', index=False)
#    df1 = gdhs.loc[(gdhs['gdhshb'] < 0) & (gdhs['gdhsjb'] < 0)]
#    df1 = df1.assign(gdhsb=df1['gdhs0']/df1['gdhs2'])
#    df1 = df1.sort_values(by='gdhsb')
#    df11 = df1.loc[(df1['ssdate'] < '20160101')]
#    df12 = df1.loc[(df1['ssdate'] >= '20160101')]
#    df1 = pd.concat([df11, df12])
#    df2 = df1.loc[(df1['gdhstb'] < 0)]
#    gdhs.to_excel(writer, sheet_name='全部', index=False)
#    df1.to_excel(writer, sheet_name='选股1', index=False)   
#    df2.to_excel(writer, sheet_name='选股2', index=False)   
#    writer.close()