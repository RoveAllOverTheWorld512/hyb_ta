# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 11:40:38 2019

@author: Administrator
"""

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="@mysqlh64y9b13",
  database='stockdata'
)

mycursor = mydb.cursor()

#mycursor.execute("CREATE DATABASE stockdata")
#mycursor.execute(
sql = """CREATE TABLE gpdmmc (
    gpdm CHAR(9) NOT NULL COMMENT '股票代码',
    gpmc CHAR(10) NOT NULL COMMENT '股票名称',
    rq date NOT NULL COMMENT '日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='股票代码名称';
"""
# 股票代码名称：数据来源
# 中证指数公司http://www.csindex.cn/
mycursor.execute(sql)

sql = """
CREATE TABLE `adj` (
  `gpdm` char(9) NOT NULL COMMENT '股票代码',
  `rq` date NOT NULL COMMENT '日期',
  `adj` double NOT NULL COMMENT '复权因子'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='日复权因子';
"""
mycursor.execute(sql)
sql = """CREATE TABLE lday (
    gpdm char(9) NOT NULL COMMENT '股票代码',
    rq date NOT NULL COMMENT '日期',
    open double DEFAULT NULL COMMENT '开盘价',
    high double DEFAULT NULL COMMENT '最高价',
    low double DEFAULT NULL COMMENT '最低价',
    close double DEFAULT NULL COMMENT '收盘价',
    vol double DEFAULT NULL COMMENT '成交量',
    amount double DEFAULT NULL COMMENT '成交额'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='日交易数据';
"""
# 日交易数据来源：通达信
mycursor.execute(sql)

sql = """
 CREATE TABLE `gdhs` (
  `gpdm` char(9) NOT NULL COMMENT '股票代码',
  `rq` date NOT NULL COMMENT '日期',
  `gdhs` int DEFAULT NULL COMMENT '股东户数',
  `aghs` int DEFAULT NULL COMMENT 'A股股东户数',
  `ggrq` date DEFAULT NULL COMMENT '公告日期',
  `sjly` varchar(255) DEFAULT NULL COMMENT '数据来源',
  `cjrq` date DEFAULT NULL COMMENT '采集日期',
  `bj` int DEFAULT NULL COMMENT '确认标记'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='股东户数';
"""
# 股东户数数据准确度不高，主要是上市公司有A股、B股和H股，很多公告数据没有分列。
# 数据来源：大智慧、东方财富
# 确认标记：1确认，确认后不再被修改。
mycursor.execute(sql)