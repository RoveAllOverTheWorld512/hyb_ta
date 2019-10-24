# -*- coding: utf-8 -*-
"""
Created on 2019-09-30 09:21:14

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""
import winreg
import os
import pickle
import struct
from pypinyin import lazy_pinyin, Style, load_single_dict
import pandas as pd
from dbfread import DBF
from .class_func import *
from .tdxconstants import *


class Tdx():
    def __init__(self):
        self.__modpath = os.path.dirname(__file__)  # 保存本模块路径
        self.__basepath = TDX_PATH  # 通达信安装文件夹
        self.__hq_cache = TDX_HQ_CACHE  # 行情高速缓存文件夹
        self.__daybasepath = TDX_DAY_BASEPATH  # 交易数据.day根文件夹
        self.__adjfactorpath = ADJ_PATH  # 复权数据文件夹
        self.__datapickle = {}    # dict数据，保存几个配置文件的MD5
        self.load_datapickle()

    @property
    def basepath(self):
        return self.__basepath

    @basepath.setter   # 使用装饰器，禁止修改
    def set_basepath(self, value):
        raise AttributeError()

    @basepath.deleter  # 使用装饰器，禁止删除
    def del_basepath(self):
        raise AttributeError()

    @property
    def daybasepath(self):
        return self.__daybasepath

    @daybasepath.setter
    def set_daybasepath(self, value):
        raise AttributeError()

    @daybasepath.deleter
    def del_daybasepath(self):
        raise AttributeError()

    @property
    def adjpath(self):
        return self.__adjfactorpath

    @adjpath.setter
    def set_adjpath(self, value):
        raise AttributeError()

    @adjpath.deleter
    def del_adjpath(self):
        raise AttributeError()

    def load_datapickle(self):
        '''
        读取datapickle文件
        '''
        pickle_fn = os.path.join(self.__modpath, 'data.pickle')
        if os.path.exists(pickle_fn):
            with open(pickle_fn, 'rb') as f:
                self.__datapickle = pickle.load(f)
                f.close()
        else:
            self.__datapickle['base'] = None
            self.__datapickle['block_gn'] = None
            self.__datapickle['block_fg'] = None
            self.__datapickle['block_zs'] = None
            self.__datapickle['shm'] = None
            self.__datapickle['szm'] = None

    def dump_datapickle(self):
        '''
        写入datapickle文件
        '''
        pickle_fn = os.path.join(self.__modpath, 'data.pickle')
        with open(pickle_fn, 'wb') as f:
            pickle.dump(self.__datapickle, f, pickle.HIGHEST_PROTOCOL)
            f.close()

    def get_fn(self, filename):
        '''获取文件名'''
        return os.path.splitext(os.path.basename(filename))[0]

    def get_tdxblk(self, lb='gn', bkpy=None):
        '''
        获取通达信板块信息

        通达信的板块信息分为三类：概念、风格和指数。分别保存在安装目录下
        T0002\hq_cache子目录,文件名分别为block_gn.dat、block_fg.dat、
        block_zs.dat

        输入参数：
            lb:类别
                "gn"(概念)，"fg"(风格)，"zs"(指数)
            bkpy:板块拼音

        输出结果：pandas DateFrame
            列名含义：
                blknm:板块名称
                blkpy:板块拼音
                blkstnum:板块股票数量
                blkst:板块股票代码串

        '''
        def py(s):
            '''
            汉字拼音大写首字母缩写
            '''
            load_single_dict({ord('长'): 'cháng,zhǎng'})  # 调整 "长" 字的拼音顺序
            return ''.join(lazy_pinyin(s, style=Style.FIRST_LETTER)).upper()

        blkfn = 'block_{}.dat'.format(lb)
        blkfn = os.path.join(self.__hq_cache, blkfn)
        fname = self.get_fn(blkfn)
        # 获取文件的MD5码
        md5 = get_filemd5(blkfn)
        oldmd5 = self.__datapickle[fname]
        # 文件内容没有变化
        pickle_fn = os.path.join(self.__modpath, f'{fname}.pickle')
        if md5 == oldmd5:
            with open(pickle_fn, 'rb') as f:
                blk = pickle.load(f)
                f.close()
            if bkpy:
                blk = blk[blk['blkpy'].str.contains(bkpy.upper())]
            return blk

        self.__datapickle[fname] = md5

        #重新提取板块
        blknm = []
        blkpy = []
        blkstnum = []
        blkst = []

        with open(blkfn, 'rb') as f:
            blknum, = struct.unpack('384xH', f.read(386))
            for i in range(blknum):
                blkname = f.read(9).strip(b'\x00').decode('GBK')
                blknm.append(blkname)

                stnum, = struct.unpack('H2x', f.read(4))
                blkstnum.append(stnum)

                stk = ''
                for j in range(stnum):
                    stkid = f.read(7).strip(b'\x00').decode('GBK')
                    stk = stk + stkid + ','

                blkst.append(stk)
                blkpy.append(py(blkname))

                f.read((400-stnum)*7)

            f.close()

        blk = pd.DataFrame({'blknm': blknm, 'blkpy': blkpy, 'blkstnum': blkstnum, 'blkst': blkst})

        # 持久化保存blk
        with open(pickle_fn, 'wb') as f:
            pickle.dump(blk, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        # 持久化保存MD5
        self.dump_datapickle()

        if bkpy:
            blk = blk[blk['blkpy'].str.contains(bkpy.upper())]

        return blk

    def get_gpfl(self, code):
        '''股票分类'''

        fldict = {'深市主板A股': '000001-001999',
                  '深市中小板A股': '002001-004999',
                  '深市创业板A股': '300001-300999',
                  '沪市主板A股': '600000-603999',
                  '沪市科创板A股': '688001-688999'}
        fl = None
        for key in fldict:
            if (fldict[key][:6] <= code <= fldict[key][7:]):
                fl = key

        return fl

    def get_gpdm(self):
        '''
        从通达信系统获取股票代码信息

        通达信系统股票代码信息保存在安装目录下T0002\hq_cache子目录
        文件名分别为shm.tnf、szm.tnf

        输出结果：pandas DateFrame
            列名含义：
                sc:市场代码，sh沪市，sz深市
                gpdm:股票代码（9位），如002294.SZ，索引
                gpmc:股票名称，如信立泰
                gppy:股票拼音，如XLT
                gplb:股票类别，如深市中小板A股
        '''
        change = False
        for sc in ('sh', 'sz'):
            fn = '{}m.tnf'.format(sc)
            fn = os.path.join(self.__hq_cache, fn)
            fname = self.get_fn(fn)

            md5 = get_filemd5(fn)
            oldmd5 = self.__datapickle[fname]
            if md5 != oldmd5:
                change = True
                self.__datapickle[fname] = md5

        pickle_fn = os.path.join(self.__modpath, 'gpdm.pickle')
        if not change:
            with open(pickle_fn, 'rb') as f:
                df = pickle.load(f)
                f.close()
            return df

        datacode = []
        for sc in ('sh', 'sz'):
            fn = '{}m.tnf'.format(sc)
            fn = os.path.join(self.__hq_cache, fn)
            f = open(fn, 'rb')
            f.seek(50)
            ss = f.read(314)
            while len(ss) > 0:
                gpdm = ss[0:6].decode('GBK')
                gpmc = ss[23:31].strip(b'\x00').decode('GBK').replace(' ', '').replace('*', '')
                gppy = ss[285:291].strip(b'\x00').decode('GBK')
                # 剔除非A股代码
                gplb = self.get_gpfl(gpdm)
                if gplb and (('沪' in gplb and sc == 'sh') or ('深' in gplb and sc == 'sz')):
                    dm = gpdm
                    gpdm = dm + '.' + sc.upper()
                    datacode.append([sc, dm, gpdm, gpmc, gppy, gplb])
                ss = f.read(314)

            f.close()

        df = pd.DataFrame(datacode, columns=['sc', 'dm', 'gpdm', 'gpmc', 'gppy', 'gplb'])
        df = df.set_index('gpdm')
        df.columns = df.columns.str.lower()

        # 持久化保存blk
        with open(pickle_fn, 'wb') as f:
            pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        # 持久化保存MD5
        self.dump_datapickle()

        return df


    def get_ssdate(self):
        '''
        从通达信系统获取股票上市时间

        通达信系统股票上市时间保存在安装目录下T0002\hq_cache子目录
        文件名base.dbf

        输出结果：pandas DateFrame
            列名含义：
                gpdm:股票代码（9位），如002294.SZ。索引
                ssdate:上市日期
        '''
        fn = os.path.join(self.__hq_cache, 'base.dbf')
        fname = self.get_fn(fn)

        md5 = get_filemd5(fn)
        oldmd5 = self.__datapickle[fname]
        pickle_fn = os.path.join(self.__modpath, f'{fname}.pickle')
        if md5 == oldmd5:
            with open(pickle_fn, 'rb') as f:
                df = pickle.load(f)
                f.close()
            return df

        self.__datapickle[fname] = md5

        table = DBF(fn, load=True)
        df = pd.DataFrame(table.records)
        df = df[['SC', 'GPDM', 'SSDATE']]
        df['GPLB'] = df['GPDM'].map(self.get_gpfl)

        # 去掉指数、基金等
        df = df[((df['SC'].str.contains('0') & df['GPLB'].str.contains('深')) | \
                 (df['SC'].str.contains('1') & df['GPLB'].str.contains('沪')))]
        # 去掉日期为空的
        df = df[~df['SSDATE'].str.startswith('  ')]

        df = df.assign(SCDM = '.SH')
        df.loc[df['SC'].str.contains('0'), 'SCDM'] = '.SZ'

        df['GPDM'] = df['GPDM'] + df['SCDM']
        df =  df.set_index('GPDM')
        df = df[['SSDATE']]
        df.columns = df.columns.str.lower()

        # 持久化保存blk
        with open(pickle_fn, 'wb') as f:
            pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        # 持久化保存MD5
        self.dump_datapickle()

        return df
