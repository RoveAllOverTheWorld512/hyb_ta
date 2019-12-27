# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 11:40:38 2019

@author: Administrator

# 数据来源
# 中证指数公司http://www.csindex.cn/

"""

import sys
import os
import mysql.connector
import xlrd
import re
import datetime
import pandas as pd
from pypinyin import lazy_pinyin, Style, load_single_dict
from stock_pandas.tdx.class_func import *
from constants_hyb import *


def createdatabase():
    '''
    创建数据库csidata
    '''
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="@mysqlh64y9b13"
    )

    mycursor = mydb.cursor()

    sql = """
    CREATE DATABASE IF NOT EXISTS csidata DEFAULT CHARACTER SET=utf8
    """
    mycursor.execute(sql)
    mycursor.execute('USE csidata;')

    sql = """
    CREATE TABLE IF NOT EXISTS `hyjtsyl` (
      `rq` date NOT NULL COMMENT '日期',
      `hydm` VARCHAR(10) NOT NULL COMMENT '行业代码',
      `hymc` VARCHAR(30) NOT NULL COMMENT '行业名称',
      `jtsyl` double DEFAULT NULL COMMENT '静态市盈率',
      `gpjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '股票家数',
      `ksjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '亏损股票家数',
      `pjjtsyl_m1` double DEFAULT NULL COMMENT '最近一个月平均静态市盈率',
      `pjjtsyl_m3` double DEFAULT NULL COMMENT '最近三个月平均静态市盈率',
      `pjjtsyl_m6` double DEFAULT NULL COMMENT '最近六个月平均静态市盈率',
      `pjjtsyl_y1` double DEFAULT NULL COMMENT '最近一年平均静态市盈率',
      UNIQUE KEY `hyjtsyl_unique` (`rq`,`hydm`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行业静态市盈率';
    """
    mycursor.execute(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS `hygdsyl` (
      `rq` date NOT NULL COMMENT '日期',
      `hydm` VARCHAR(10) NOT NULL COMMENT '行业代码',
      `hymc` VARCHAR(30) NOT NULL COMMENT '行业名称',
      `gdsyl` double DEFAULT NULL COMMENT '滚动市盈率',
      `gpjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '股票家数',
      `ksjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '亏损股票家数',
      `pjgdsyl_m1` double DEFAULT NULL COMMENT '最近一个月平均滚动市盈率',
      `pjgdsyl_m3` double DEFAULT NULL COMMENT '最近三个月平均滚动市盈率',
      `pjgdsyl_m6` double DEFAULT NULL COMMENT '最近六个月平均滚动市盈率',
      `pjgdsyl_y1` double DEFAULT NULL COMMENT '最近一年平均滚动市盈率',
      UNIQUE KEY `hygdsyl_unique` (`rq`,`hydm`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行业滚动市盈率';
    """
    mycursor.execute(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS `hysjl` (
      `rq` date NOT NULL COMMENT '日期',
      `hydm` VARCHAR(10) NOT NULL COMMENT '行业代码',
      `hymc` VARCHAR(30) NOT NULL COMMENT '行业名称',
      `syl` double DEFAULT NULL COMMENT '市净率',
      `gpjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '股票家数',
      `fzcjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '负资产股票家数',
      `pjsjl_m1` double DEFAULT NULL COMMENT '最近一个月平均市净率',
      `pjsjl_m3` double DEFAULT NULL COMMENT '最近三个月平均市净率',
      `pjsjl_m6` double DEFAULT NULL COMMENT '最近六个月平均市净率',
      `pjsjl_y1` double DEFAULT NULL COMMENT '最近一年平均市净率',
      UNIQUE KEY `hysjl_unique` (`rq`,`hydm`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行业市净率';
    """
    mycursor.execute(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS `hygxl` (
      `rq` date NOT NULL COMMENT '日期',
      `hydm` VARCHAR(10) NOT NULL COMMENT '行业代码',
      `hymc` VARCHAR(30) NOT NULL COMMENT '行业名称',
      `gxl` double DEFAULT NULL COMMENT '股息率',
      `gpjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '股票家数',
      `wfhjs` smallint(5) UNSIGNED DEFAULT NULL COMMENT '未分红股票家数',
      `pjgxl_m1` double DEFAULT NULL COMMENT '最近一个月平均股息率',
      `pjgxl_m3` double DEFAULT NULL COMMENT '最近三个月平均股息率',
      `pjgxl_m6` double DEFAULT NULL COMMENT '最近六个月平均股息率',
      `pjgxl_y1` double DEFAULT NULL COMMENT '最近一年平均股息率',
      UNIQUE KEY `hygxl_unique` (`rq`,`hydm`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='行业股息率';
    """
    mycursor.execute(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS `ggsj` (
      `rq` date NOT NULL COMMENT '日期',
      `gpdm` CHAR(9) NOT NULL COMMENT '股票代码',
      `gpmc` VARCHAR(30) NOT NULL COMMENT '股票名称',
      `hydm1` VARCHAR(10) DEFAULT NULL COMMENT '一级行业代码',
      `hymc1` VARCHAR(30) DEFAULT NULL COMMENT '一级行业名称',
      `hydm2` VARCHAR(10) DEFAULT NULL COMMENT '二级行业代码',
      `hymc2` VARCHAR(30) DEFAULT NULL COMMENT '二级行业名称',
      `hydm3` VARCHAR(10) DEFAULT NULL COMMENT '三级行业代码',
      `hymc3` VARCHAR(30) DEFAULT NULL COMMENT '三级行业名称',
      `hydm4` VARCHAR(10) DEFAULT NULL COMMENT '四级行业代码',
      `hymc4` VARCHAR(30) DEFAULT NULL COMMENT '四级行业名称',
      `jtsyl` double DEFAULT NULL COMMENT '静态市盈率',
      `gdsyl` double DEFAULT NULL COMMENT '滚动市盈率',
      `sjl` double DEFAULT NULL COMMENT '市净率',
      `gxl` double DEFAULT NULL COMMENT '股息率',
      UNIQUE KEY `ggsj_unique` (`rq`,`gpdm`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='个股数据';
    """
    mycursor.execute(sql)

    sql = """
    CREATE TABLE IF NOT EXISTS `ybcrq` (
      `rq` date NOT NULL COMMENT '日期',
      PRIMARY KEY (`rq`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='已保存日期';    """
    mycursor.execute(sql)


def py(s):
    '''
    汉字拼音大写首字母缩写
    '''
    load_single_dict({ord('长'): 'cháng,zhǎng'})  # 调整 "长" 字的拼音顺序
    return ''.join(lazy_pinyin(s, style=Style.FIRST_LETTER))


def get_rqs():
    '''
    读取未保存日期
    '''
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="@mysqlh64y9b13",
        database="csidata"
    )
    mycursor = mydb.cursor()
    sql = 'select rq from ybcrq;'
    mycursor.execute(sql)
    res = mycursor.fetchall()
    mydb.close()
    ybcrq = [e[0].strftime('%Y%m%d') for e in res]

    files = os.listdir(PE_PATH)
    fs = [re.findall(r'.*(\d{8})\.xls', e) for e in files]
    rqs = [e[0] for e in fs if e != []]

    return list_sub(rqs, ybcrq)


def get_csisylxls():
    '''
    从csi市盈率表提取个股数据
    '''
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="@mysqlh64y9b13",
        database="csidata"
    )
    mycursor = mydb.cursor()

    sht = {'hyjtsyl': '中证行业静态市盈率',
           'hygdsyl': '中证行业滚动市盈率',
           'hysjl': '中证行业市净率',
           'hygxl': '中证行业股息率',
           'ggsj': '个股数据'}

    fld = {'hyjtsyl': ["hydm", "hymc", "jtsyl", "gpjs", "ksjs",
                       "pjjtsyl_m1", "pjjtsyl_m3", "pjjtsyl_m6",
                       "pjjtsyl_y1", "rq"],
           'hygdsyl': ["hydm", "hymc", "gdsyl", "gpjs", "ksjs", "pjgdsyl_m1",
                       "pjgdsyl_m3", "pjgdsyl_m6", "pjgdsyl_y1", "rq"],
           'hysjl': ["hydm", "hymc", "syl", "gpjs", "fzcjs",
                     "pjsjl_m1", "pjsjl_m3", "pjsjl_m6", "pjsjl_y1", "rq"],
           'hygxl': ["hydm", "hymc", "gxl", "gpjs", "wfhjs", "pjgxl_m1",
                     "pjgxl_m3", "pjgxl_m6", "pjgxl_y1", "rq"],
           'ggsj': ["gpdm", "gpmc", "hydm1", "hymc1", "hydm2", "hymc2",
                    "hydm3", "hymc3", "hydm4", "hymc4", "jtsyl", "gdsyl",
                    "sjl", "gxl", "rq"]}

    rqs = get_rqs()  # 获取未保存日期列表

    for rq in rqs:
        fn = os.path.join(PE_PATH, f'csi{rq}.xls')
        print(fn)
        try:
            wb = xlrd.open_workbook(fn, encoding_override="cp1252")
        except BaseException:
            continue
        for sh in sht:
            print(sh, sht[sh])

            table = wb.sheet_by_name(sht[sh])
            nrows = table.nrows  # 行数
            data = []

            row = table.row_values(0)  # 列名
            cols = [py(e).replace('\n', '') for e in row]  # 将列名转换成汉字拼音首字母
            data = [table.row_values(i) for i in range(1, nrows)]
            df = pd.DataFrame(data, columns=cols)

            df['rq'] = rq  # 注意顺序，这列会加在df的最右侧

            if sh == 'ggsj':
                df['zqdm'] = df['zqdm'].map(
                    lambda x: x + ('.SH' if x[0] == '6' else '.SZ'))
            cols = fld[sh]
            df.columns = cols  # 更改列名
            data = df.values.tolist()
            # 将"-"用None替换
            data = [[None if e == '-' else e for e in d] for d in data]
            flds1 = ','.join(cols)
            flds2 = ('%s,' * len(cols))[:-1]
            sql = f'INSERT IGNORE INTO {sh} ({flds1}) VALUES ({flds2});'
            mycursor.executemany(sql, data)

        sql = f'INSERT IGNORE INTO ybcrq VALUES ("{rq}");'
        mycursor.execute(sql)
        mydb.commit()

    mycursor.close()
    mydb.close()
    return True


def count_time(func):
    '''
    函数运行计时装饰器
    '''
    def int_time(*args, **kwargs):
        start_time = datetime.datetime.now()  # 程序开始时间
        func()
        over_time = datetime.datetime.now()   # 程序结束时间
        total_time = (over_time - start_time).total_seconds()
        print('程序共计%s秒' % total_time)
    return int_time


@count_time
def main():
    print('>>>>开始计算函数运行时间')
    get_csisylxls()


if __name__ == '__main__':
    createdatabase()
    main()
