# -*- coding: utf-8 -*-
"""
Created on 2019-10-02 11:51:04

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

结构可以从文件或字节字符串中读取。

通达信的日线数据格式如下：
每32个字节为一天数据
每4个字节为一个字段，每个字段内低字节在前
00 ~ 03 字节：年月日, 整型
04 ~ 07 字节：开盘价*100， 整型
08 ~ 11 字节：最高价*100, 整型
12 ~ 15 字节：最低价*100, 整型
16 ~ 19 字节：收盘价*100, 整型
20 ~ 23 字节：成交额（元），float型
24 ~ 27 字节：成交量（股），整型
28 ~ 31 字节：（保留）

struct --- 将字节串解读为打包的二进制数据
https://docs.python.org/zh-cn/3.7/library/struct.html


"""

import os
import struct
import dateutil.parser
import pandas as pd
import re
from .tdxcfg import Tdx
from .class_func import *
from .tdxconstants import *

class Tdxday(object):
    """TDX .day文件
    输入参数:filename,形如sh600000.day
    输入参数有下列几种：
    1、6位数字，必须是A股代码。如002294、000001、600000。处理方法：在股票代码表中查询
        对应信息，如未发现，抛出错误信息。
    2、8位字符，2位市场代码字母sh或sz，6位数字。除包含A股外，还包括基金和指数
        如sh502011、sz399901。处理方法：在股票代码表中查询，如为A股代码，按股票流程处理。
        如不是，按指数或基金处理。补齐.day后按下条情况处理。
    3、12位字符串，形如sh600000.day，文件名。在默认路径查找数据文件
    4、全路径字符串。处理方法：直接处理。

    """
    def __init__(self, filename):
        self._filename = filename  # 保存传入的参数
        self.dayfilename = None  # .day数据文件带路径全名
        self.argvtype = None  # 参数类型
        self.market = None   # 市场代码：sh沪、sz深
        self.dm = None   # 股票代码(6位）、也可能是基金或指数代码
        # 以下为A股信息，非股票则全为None
        self.gpdm = None   # 股票代码(9位)
        self.gpmc = None   # 股票名称
        self.gppy = None   # 股票拼音
        self.gplb = None   # 股票类别
        self.adjcsvfn = None   # 复权文件名
        self.check_filename()

    def check_filename(self):
        '''
        检查输入文件名是否符合规范，提取股票基本信息
        '''
        check = re.search('(\d{6})', self._filename)
        if not check:
            raise CustomError('参数中不包含6位数字代码')
        dirname = os.path.dirname(self._filename)
        if not dirname:  # 不带有路径的枪
            if len(self._filename) == 6:  # 6位
                sc, fl = get_gpfl(self._filename)  # 查询是否为A股
                if sc:
                    self.argvtype = 1
                    self.market = sc
                    self.dm = self._filename
                else:
                    raise CustomError('不是A股代码')
            elif len(self._filename) == 8:  # 8位
                check = re.search('(s[h|z])(\d{6})', self._filename)
                if not check:
                    raise CustomError('不是形如【sh600000】8位字符数字代码')
                else:
                    self.argvtype = 2
                    self.market, self.dm = check.groups()        
            elif len(self._filename) == 12:  # 12位
                check = re.search('(s[h|z])(\d{6})\.day', self._filename)
                if not check:
                    raise CustomError('不是形如【sh600000.day】12位字符数字代码')
                else:
                    self.argvtype = 3
                    self.market, self.dm = check.groups()        
            else:
                raise CustomError('输入参数有误！')
        else:  # 带全路径的参数
            check = re.search('(s[h|z])(\d{6})\.day', self._filename)
            if not check:
                raise CustomError('不包含形如【sh600000.day】12位字符数字代码')
            self.argvtype = 4
            self.market, self.dm = check.groups()        
            self.dayfilename = self._filename
        # 检测是否为A股
        tdx = Tdx()
        gpdmb = tdx.get_gpdm()
        gpinfo = gpdmb.loc[(gpdmb['dm'] == self.dm) & (gpdmb['sc'] == self.market), :]
        # 是否A股
        if len(gpinfo) == 1:  # 是A股
            self.gpdm = gpinfo.index[0]
            self.gpmc = gpinfo['gpmc'][0]
            self.gppy = gpinfo['gppy'][0]
            self.gplb = gpinfo['gplb'][0]
            self.adjcsvfn = os.path.join(tdx.adjpath,
                                         self.dm + '.csv')
            if self.argvtype in (1, 2, 3):
                self.dayfilename = os.path.join(tdx.daybasepath,
                                                f'{self.market}\\lday\\{self.market}{self.dm}.day')
        else:  # 不是A股
            self.dayfilename = os.path.join(tdx.daybasepath,
                                            f'{self.market}\\lday\\{self.market}{self.dm}.day')
            
        # 检测数据文件是否存在
        if not os.path.exists(self.dayfilename):  # 指定文件不存在
            self.dayfilename = None
#            raise CustomError('数据文件不存在！')

    def get_data(self):
        '''
        提取交易原始数据
        '''
        df = get_data(self.dayfilename)
        df.scdm = self.market
        df.gpdm = self.gpdm
        df.gpmc = self.gpmc
        df.dm = self.dm
        df.adjcsvfn = self.adjcsvfn
        return df

    def get_adjfactor(self):
        '''
        提取复权因子，计算前复权系数
        '''
        if self.adjcsvfn:
            return get_adjfactor(self.adjcsvfn)

        return None

    def get_qfqdata(self, start=None, end=None, otype='ohlcv'):
        '''
        前复权股价
        otype输出类型：ohlc,ohlcv,ohlcav 其中的ohlc均为前复权值，其他类型ohlc为原始值
        '''
        outtype = {'ohlc': ['open', 'high', 'low', 'close'],
                   'ohlcv': ['open', 'high', 'low', 'close', 'volume'],
                   'ohlcav': ['open', 'high', 'low', 'close', 'amount',
                              'volume'],
                   'ohlcv_ac': ['open', 'high', 'low', 'close', 'volume',
                                'adj_close'],
                   'ohlcav_ac': ['open', 'high', 'low', 'close', 'amount',
                                 'volume', 'adj_close'],
                   'ohlcv_af': ['open', 'high', 'low', 'close', 'volume',
                                'adj_factor'],
                   'ohlcav_af': ['open', 'high', 'low', 'close', 'amount',
                                 'volume', 'adj_factor']}
        df = self.get_data()
        
        if self.adjcsvfn:
            adjdf = get_adjfactor(self.adjcsvfn)
            df = df.join(adjdf)
        else:
            df['adj_factor'] = 1

        if otype in ('ohlc', 'ohlcv', 'ohlcav'):
            columns = ['open', 'high', 'low', 'close']
            df[columns] = df[columns].mul(df['adj_factor'], axis=0)
            df = df.dropna(subset=columns)
        elif otype in ('ohlc_ac', 'ohlcv_ac'):
            df['adj_close'] = df.assign(adj_close=df['close']*df['adj_factor'])
            df = df.dropna(subset='adj_colse')

        df = df.sort_index()

        columns = outtype[otype]
        df = df[columns]
        if not df.empty:
            try:
                start = pd.to_datetime(start)
            except ValueError:
                start = None
            try:
                end = pd.to_datetime(end)
            except ValueError:
                end = None
            if not start:
                start = df.index[0]
            if not end:
                end = df.index[-1]
            df = df[start:end]
        df.scdm = self.market
        df.gpdm = self.gpdm
        df.gpmc = self.gpmc
        df.dm = self.dm
        df.adjcsvfn = self.adjcsvfn
        return df

    def get_data_pybacktest(self, start=None, end=None):
        df = self.get_qfqdata()
        columns = 'open,high,low,close'.split(',')
        df = df[columns]
        columns = 'O,H,L,C'.split(',')
        df.columns = columns
        df = df.sort_index()
        try:
            start = pd.to_datetime(start)
        except ValueError:
            start = None
        try:
            end = pd.to_datetime(end)
        except ValueError:
            end = None
        if not start:
            start = df.index[0]
        if not end:
            end = df.index[-1]
        df = df[start:end]
        df.scdm = self.market
        df.gpdm = self.gpdm
        df.gpmc = self.gpmc
        df.dm = self.dm
        df.adjcsvfn = self.adjcsvfn
        return df

    def get_data_backtrader(self, start=None, end=None):
        df = self.get_qfqdata(otype='ohlcv')
        df['openinterest'] = 0
        columns = 'open,close,high,low,volume,openinterest'.split(',')
        df = df[columns]
        df = df.sort_index()
        try:
            start = pd.to_datetime(start)
        except ValueError:
            start = None
        try:
            end = pd.to_datetime(end)
        except ValueError:
            end = None
        if not start:
            start = df.index[0]
        if not end:
            end = df.index[-1]
        df = df[start:end]
        df.scdm = self.market
        df.gpdm = self.gpdm
        df.gpmc = self.gpmc
        df.dm = self.dm
        df.adjcsvfn = self.adjcsvfn
        return df

    def get_data_yahoo(self, start=None, end=None):
        '''
        Yahoo格式的数据分段为：
        日线数据：Date,Open,High,Low,Close,Volume,Adj Close
        分钟数据：Date Time,Open,High,Low,Close,Volume,Adj Close
        '''
        df = self.get_data()
        try:
            start = pd.to_datetime(start)
        except ValueError:
            start = None
        try:
            end = pd.to_datetime(end)
        except ValueError:
            end = None
        if not start:
            start = df.index[0]
        if not end:
            end = df.index[-1]
        df = df[start:end]

        if self.adjcsvfn:
            adjdf = get_adjfactor(self.adjcsvfn)        
            df = df.join(adjdf)
        else:
            df['adj_factor'] = 1

        df = df.assign(adj_close=df['close']*df['adj_factor'])
        df = df.sort_index()
        df = df.reset_index()
        columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'adj_close']        
        df = df[columns]
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
        df.columns = columns
        df = df[start:end]
        df.scdm = self.market
        df.gpdm = self.gpdm
        df.gpmc = self.gpmc
        df.dm = self.dm
        df.adjcsvfn = self.adjcsvfn
        return df
