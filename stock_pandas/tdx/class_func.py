# -*- coding: utf-8 -*-
"""
Created on 2019-10-03 16:29:00

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

本模块为自定义类和函数

"""

import os
import time
import hashlib
import pandas as pd
import numpy as np
import dateutil.parser
import struct
import winreg
import datetime
from io import StringIO
from urllib import request


class CustomError(Exception):
    '''
    自定义错误异常
    '''
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


def get_tdxdir():
    '''
    获取本机安装的通达信文件夹
    返回值，如'd:\\new_hxzq_hc'
    '''
    value = None
    tdxreg = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\华西证券华彩人生"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, tdxreg)
        value, type = winreg.QueryValueEx(key, "InstallLocation")
    except FileNotFoundError:
        raise CustomError("本机未安装【华西证券华彩人生】软件系统。")

    return os.path.abspath(value)


def get_filemd5(filename):
    '''
    获取文件的MD5码
    '''
    md5obj = hashlib.md5()
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024*1024)  # 每次读入1M
                if not data:
                    break
                md5obj.update(data)
            hash = md5obj.hexdigest()
        return hash
    else:
        raise CustomError(f'{filename}文件不存在')


def get_filemtime(filename):
    '''
    获取文件创建、修改时间
    '''

    ltime = None
    if os.path.exists(filename):
        mtime = os.path.getmtime(filename)
        ltime = time.strftime("%Y%m%d%H%M", time.localtime(mtime))
    else:
        print(f'{filename}不存在，请确认。')
    return ltime


def get_data(filename):

    _columns = ['date', 'open', 'high', 'low', 'close',
                'amount', 'volume']
    df = pd.DataFrame(columns=_columns)
    if (filename is None) or (not os.path.exists(filename)):
        print(f'{filename}不存在，请确认。')
        df.remarks = '数据文件不存在'
        return df

    # 文件存在，读取数据
    _format = 'iiiiifii'
    with open(filename, "rb") as f:
        data = f.read()
        f.close()

    days = int(len(data)/32)  # 数据文件交易日天数

    records = []
    for i in range(days):
        dat = data[i * 32: (i + 1) * 32]
        rq, kp, zg, zd, sp, cje, cjl, tmp = struct.unpack(_format, dat)
        rq = dateutil.parser.parse(str(rq)).strftime("%Y-%m-%d")
        kp = kp/100.00
        zg = zg/100.00
        zd = zd/100.00
        sp = sp/100.00
        cje = cje/100000000.00     # 亿元
        cjl = cjl/10000.00         # 万股
        records.append([rq, kp, zg, zd, sp, cje, cjl])

    df = pd.DataFrame(records, columns=_columns)
    df = df.drop_duplicates()  # 去重
    df = df.dropna(thresh=5)
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index)
    df.remarks = '数据提取成功'
    return df


def get_adjfactor(filename):
    '''
    提取复权因子，计算前复权系数
    参数:filename,复权因子.csv文件，从tushare下载。
        文件格式如下：
        datetime,adj_factor
        2019-09-18,12.714
        2019-09-17,12.714
        2019-09-16,12.714

    '''
    if (filename is None) or (not os.path.exists(filename)):
        _columns = ['adj_factor']
        today = datetime.datetime.now()
        ndtoday = today + datetime.timedelta(-30)
        dt1 = ndtoday.strftime("%Y-%m-%d")
        dt2 = today.strftime("%Y-%m-%d")
        index = pd.date_range(dt1, dt2, freq='B')
        df = pd.DataFrame(1.00, index=index, columns=_columns)
        df.index.name = 'date'
        return df

    df = pd.read_csv(filename, parse_dates=True, infer_datetime_format=True)
    df = df.set_index('datetime')
    df = df.sort_index(ascending=True)
    # 补齐日期
    dt1 = df.index[0]
    dt2 = datetime.datetime.now().strftime("%Y-%m-%d")
#    dt2 = df.index[len(df)-1]
    index = pd.date_range(dt1, dt2, freq='B')
    df1 = pd.DataFrame(index=index)
    df = df1.join(df)
    df.fillna(method='ffill', inplace=True)
    # 前复权
    df = df.sort_index(ascending=False)
    a = df.iloc[0][0]
    df = df/a
    df.index.name = 'date'
    df.remarks = '数据提取成功'

    return df


def get_gpfl(code):
    '''
    股票分类:
        参数：code
        返回：(sc, fl)
        如果不是A股，返回(None,None)
        沪市A股，返回('sh','沪市...')，深市A股，返回('sz','深市...')
    '''
    fldict = {'深市主板A股': '000001-001999',
              '深市中小板A股': '002001-004999',
              '深市创业板A股': '300001-300999',
              '沪市主板A股': '600000-603999',
              '沪市科创板A股': '688001-688999'}
    sc = None
    fl = None
    for key in fldict:
        if (fldict[key][:6] <= code <= fldict[key][7:]):
            fl = key
    if fl:
        sc = 'sh' if '沪' in fl else 'sz'
    return sc, fl


def nd_today(n):
    '''
    返回n天前到今天的两个日期字符串yyyymmdd,yyyymmdd
    n=0,则均为今日
    '''
    today = datetime.datetime.now()
    ndtoday = today + datetime.timedelta(-n)
    return ndtoday.strftime("%Y%m%d"), today.strftime("%Y%m%d")


def lastopenday(dt=None):
    '''
    获取最新交易日，如果当天是交易日，在16:00后用当天。
    '''
    df = openday_df()
    now = datetime.datetime.now().strftime("%H%M")
    if dt is None:
        dt = datetime.datetime.today()
    else:
        dt = dateutil.parser.parse(dt)
    dt = dt.strftime("%Y-%m-%d")
    r = df.loc[dt]
    if now < '1600' or r.isOpen == 0:
        lastopen = r.pretrade_date
    else:
        lastopen = dt

    return lastopen


def openday_df():
    '''
    开始日列表
    根据tushare/stock/cons.py，
    ALL_CAL_FILE = '%s%s/tsdata/calAll.csv'%(P_TYPE['http'], DOMAINS['oss'])
    calAll.csv从http://file.tushare.org/tsdata/calAll.csv下载
    '''
    filename = 'calAll.csv'
    if not os.path.exists(filename):
        url = 'http://file.tushare.org/tsdata/calAll.csv'
        req = request.Request(url)
        text = request.urlopen(req, timeout=10).read().decode('GBK')
        filename = StringIO(text)

    df = pd.read_csv(filename, index_col=0, parse_dates=True,
                     infer_datetime_format=True)
    df = df.sort_index()
    df['pretrade_date'] = df.index.strftime('%Y-%m-%d')
    df.loc[df['isOpen'] == 0, 'pretrade_date'] = np.NaN
    df['pretrade_date'] = df['pretrade_date'].fillna(method='ffill')
    df['pretrade_date'] = df['pretrade_date'].shift(1)

    return df


if __name__ == '__main__':
    fn = r'd:\tdx\shlday\sh601360.day'
    df = get_data(fn)
#    dt = '20191001'
#    print(lastopenday(dt))
