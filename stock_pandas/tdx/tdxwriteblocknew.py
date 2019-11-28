# -*- coding: utf-8 -*-
"""
Created on 2019-11-26 13:32:55

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193


"""

import os
import pandas as pd
import struct
from collections import OrderedDict
from .tdxconstants import *


class CustomerBlockWriter(object):
    def __init__(self):
        self.__modpath = os.path.dirname(__file__)  # 保存本模块路径
        self.__basepath = TDX_PATH  # 通达信安装文件夹
        self.__blocknew = TDX_BLOCKNEW  # 自定义板块文件夹
        self.__hq_cache = TDX_HQ_CACHE  # 行情高速缓存文件夹

    def get_cfg(self):
        '''
        读取blocknew.cfg，以pandas.DataFrame格式返回
        '''
        fname = self.__blocknew
        result = []
        if not os.path.isdir(fname):
            raise Exception('not a directory')
        block_file = '/'.join([fname, 'blocknew.cfg'])
        if not os.path.exists(block_file):
            raise Exception('file not exists')
        with open(block_file, 'rb') as f:
            block_data = f.read()
            pos = 0
            result = []
            while pos < len(block_data):
                n1 = block_data[pos:pos + 50].decode('gbk', 'ignore').rstrip("\x00")
                n2 = block_data[pos + 50: pos + 120].decode('gbk', 'ignore').rstrip("\x00")
                pos = pos + 120
                n1 = n1.split('\x00')[0]
                n2 = n2.split('\x00')[0]
                bf = '/'.join([fname, n2 + '.blk'])
                if not os.path.exists(bf):
                    raise Exception('file not exists')
                result.append(
                    OrderedDict([("blockname", n1),
                                 ("block_type", n2)])
                )
            f.close()
        df = pd.DataFrame(result)
        return df

    def write_cfg(self, blockname, block_type, rewrite=True, pos=1):
        fname = self.__blocknew
        if not os.path.isdir(fname):
            raise Exception('not a directory')
        block_file = '/'.join([fname, 'blocknew.cfg'])
        df = self.get_cfg()  # 读取blocknew.cfg
        block_type = block_type.upper()  # 板块简称变大写
        if not rewrite and (block_type in df['block_type'].tolist() or
                            blockname in df['blockname'].tolist()):
            raise Exception('blockname or blocktype exists. No rewrite!')

        df = df.reset_index()  # 生成排序号
        df['index'] = df['index'] + 1  # 排序号+1
        # 将pos位置腾出来
        df.loc[(df['index'] >= pos), 'index'] = df['index'] + 1
        # 板块简称已存在的，板块名称改名，换位置
        if block_type in df['block_type'].tolist():
            df.loc[(df['block_type'] == block_type), 'blockname'] = blockname
            df.loc[(df['block_type'] == block_type), 'index'] = pos
        # 板块名称已存在的
        elif blockname in df['blockname'].tolist():
            df.loc[(df['blockname'] == blockname), 'block_type'] = block_type
            df.loc[(df['blockname'] == blockname), 'index'] = pos
        else:
            df = df.append(pd.Series({"index": pos,
                                      "blockname": blockname,
                                      'block_type': block_type}),
                           ignore_index=True)
        df = df.sort_values(by='index')

        block_file = '/'.join([fname, 'blocknew.cfg'])
        with open(block_file, 'wb') as f:
            for i, row in df.iterrows():
                n1 = row.blockname
                n2 = row.block_type
                n1 = n1.ljust(50, '\x00').encode('GBK')
                n2 = n2.ljust(70, '\x00').encode('GBK')
                s = struct.pack('<50s70s', n1, n2)
                f.write(s)
            f.close()
        return True

    def write_blk(self, block_type, codelist, rewrite=True):
        '''
        参数codelist：
        1002294
        1600000
        '''
        fname = self.__blocknew
        bf = '/'.join([fname, block_type + '.blk'])
        if not rewrite and os.path.exists(bf):
            raise Exception('blockfile exists. No rewrite!')
        with open(bf, 'w+') as f:
            f.writelines(codelist)
            f.close()
        return True

    def gen_codelist(self, codelist):
        '''
        参数codelist有多种形式：
        1.str
        002294.SZ,600000.SH
        002294,600000
        SZ002294,SH600000
        2.list
        3.pd.Series
        返回：
        0002294
        1600000
        '''
        if isinstance(codelist, str):
            lst = codelist.split(',')
        elif isinstance(codelist, pd.Series):
            lst = codelist.tolist()
        elif isinstance(codelist, list):
            lst = codelist
        lst = [e.upper() for e in lst]  # 转大写
        if (len(lst[0]) == 9) and (lst[0][-3:-1] == '.S'):
            lst = ['0' + e[:6] if (e[-1] == 'Z') else '1' + e[:6] for e in lst]
        elif (len(lst[0]) == 8) and (lst[0][0] == 'S'):
            lst = ['0' + e[2:] if (e[1] == 'Z') else '1' + e[2:] for e in lst]
        elif len(lst[0]) == 6:
            lst = ['1' + e if (e[0] == '6') else '0' + e for e in lst]
        lst = [line + '\n' for line in lst]

        return lst

    def save_blocknew(self, blockname, block_type, codelist, rewrite, pos):
        fname = self.__blocknew
        codelist = self.gen_codelist(codelist)
        if self.write_cfg(blockname, block_type, rewrite, pos):
            if self.write_blk(block_type, codelist, rewrite):
                print('OK')
        else:
            print('ERROR')
        return

    def delete_blkfn(self):
        '''
        删除不在blocknew.cfg中的.blk文件
        '''
        fname = self.__blocknew
        df = self.get_cfg()  # 读取blocknew.cfg
        blks = df['block_type'].tolist()
        # 获取文件列表
        files = os.listdir(fname)
        for fn in files:
            if fn[-4:].upper() == '.BLK':
                if (fn != 'ZXG.blk') and (fn[:-4] not in blks):
                    os.remove('/'.join([fname, fn]))
        return True


if __name__ == '__main__':

    bkn = CustomerBlockWriter()
    bkn.delete_blkfn()
#    blockname = '测试'
#    block_type = 'TEST'
#    pos = 3
#    # df12从其他程序生成的
#    codelist = df12['gpdm']
#    rewrite = True
#    bkn.save_blocknew(blockname, block_type, codelist, rewrite, pos)
