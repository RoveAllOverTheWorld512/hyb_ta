# -*- coding: utf-8 -*-
"""
Created on 2019-12-17 22:01:24

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""
import subprocess
import datetime


def prgrun(msg, prg):
    print(f'正在处理【{msg}】，请等候……')
    now1 = datetime.datetime.now()
    print('开始运行时间：%s' % now1.strftime('%H:%M:%S'))

    cmd_re = subprocess.run(
            f"pythonw.exe {prg}",
            shell=True, stdout=subprocess.PIPE)
    print(cmd_re.stdout.decode('GBK'))
    now2 = datetime.datetime.now()
    t = (now2 - now1).seconds / 60
    print('所用时间：%5.2f分钟' % t)
    return True


if __name__ == '__main__':
#    msg = '提取股东户数，大概需要20分钟'
#    prg = r'D:\selestock\dzh-gdhs2sqlite.py'
#    prgrun(msg, prg)
#
#    msg = '分析股东户数变化，大概需要1分钟'
#    prg = r'D:\pandas-ta_project\stock_pandas\misc\gdhs.py'
#    prgrun(msg, prg)
#
#    msg = '双底研究，大概需要70分钟'
#    prg = r'D:\pandas-ta_project\double_bottom_study.py'
#    prgrun(msg, prg)
#
#    msg = '双底研究，生成通达信自定义板块，大概需要1分钟'
#    prg = r'D:\pandas-ta_project\today_sele.py'
#    prgrun(msg, prg)

    msg = '下载市盈率，大概需要1分钟'
    prg = r'd:\selestock\dlsyl.py'
    prgrun(msg, prg)

    msg = '市盈率入库，大概需要1分钟'
    prg = r'd:\hyb\syl2sqlite.py'
    prgrun(msg, prg)

    msg = '股票改名信息入库，大概需要1分钟'
    prg = r'd:\pandas-ta_project\stock_pandas\misc\gpgm.py'
    prgrun(msg, prg)
