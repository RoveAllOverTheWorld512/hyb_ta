# -*- coding: utf-8 -*-
"""
从大智慧F10提取股东户数导入Sqlite数据库

参考资料：
Python多线程爬虫与多种数据存储方式实现
https://blog.csdn.net/fei347795790/article/details/99679268

多种方法实现Python线程池
http://www.360doc.com/content/19/0818/10/12765144_855617590.shtml

[python] ThreadPoolExecutor线程池
https://www.jianshu.com/p/b9b3d66aa0be

python操作sqlite示例(支持多进程/线程同时操作)
https://www.cnblogs.com/Jerryshome/archive/2013/01/30/2882931.html

高效运用SQLite和Python
https://itdiffer.com/article/39

Multi-threaded SQLite without the OperationalErrors
http://charlesleifer.com/blog/multi-threaded-sqlite-without-the-operationalerrors/

peewee
http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#sqliteq

Going Fast with SQLite and Python
http://charlesleifer.com/blog/going-fast-with-sqlite-and-python/

"""
from pyquery import PyQuery as pq
import datetime
import time
import sqlite3
import socket
import selestock as my
import sys

########################################################################
#从大智慧网F10获取股东户数
########################################################################
def get_gdhs(gpdm):

    sc=my.scdm(gpdm)
    gpdm=my.sgpdm(gpdm)
    
    data=[]
    url = 'http://webf10.gw.com.cn/'+sc+'/B10/'+sc+gpdm+'_B10.html'

    try :
        html = pq(url,encoding="utf-8")
        #第3个区块
        #sect = pq(html('section').eq(2).html())
        #提取预测明细
        sect=html('section').filter('#股东人数').html()
        tr=pq(sect)

        for i in range(1,len(tr('ul'))):
            
            il=tr('ul').eq(i).text()
            il=il.split('\n')
            rq=il[0]
            gdhs=il[1]
    
            data.append([my.lgpdm(gpdm),rq,gdhs])
    except : 
        print("出错退出")

    return data
    
    
########################################################################
#从大智慧网F10获十大流通股东
########################################################################
def get_sdltgd(gpdm):

    '''
    CREATE TABLE [LTG](
      [GPDM] TEXT NOT NULL, 
      [RQ] TEXT NOT NULL, 
      [LTG] REAL, 
      [SDGDCG] REAL, 
      [SDGDZB] REAL, 
      [SHCG] REAL, 
      [DGDGS] INT DEFAULT 10);
    
    CREATE UNIQUE INDEX [GPDM_RQ_LTG]
    ON [LTG](
      [GPDM], 
      [RQ]);
    '''

    sc=my.scdm(gpdm)
    gpdm=my.sgpdm(gpdm)
    
    data=[]

    url = 'http://webf10.gw.com.cn/'+sc+'/B10/'+sc+gpdm+'_B10.html'

    try :
        html = pq(url,encoding="utf-8")

        sect=html('section').filter('#十大流通股东').html()
        divs=pq(sect)

        divs=divs('div.sdltgdTb')
        for i in range(len(divs)):
            div=divs.eq(i)
            rq=div.attr('id')[10:20]
            con=pq(div)
    
    #        ljcg=con('p').text()
    #        cg=re.findall('累计持有：(.+)万股，累计占总流通股比：(.+)\%',ljcg)
    #        dgdcg=eval(cg[0][0])
    #        dgdzb=eval(cg[0][1])
    #        ltg=round(dgdcg/dgdzb*100,2)
    #        shcg=round(ltg-dgdcg,2)
    #        data.append([my.lgpdm(gpdm),rq,ltg,dgdcg,dgdzb,shcg,10])
    
            tbl=con('table').eq(0)
            tbl=pq(tbl)
            sl=0
            bl=0
            gs=0
            for j in range(1,len(tbl('tr'))):
                row=pq(tbl('tr').eq(j))
                row=row('td')
                cgsl=row.eq(1).text()
                cgbl=row.eq(3).text()
                cglx=row.eq(4).text()
                if cglx=='流通A股' and my.str2float_none(cgsl)!=None and my.str2float_none(cgbl)!=None:
                    sl=sl+float(cgsl)
                    bl=bl+float(cgbl)
                    gs=gs+1
                    
            if gs>0:
                ltg=round(sl/bl*100,2)
                sl=round(sl,2)
                bl=round(bl,2)
                sh=round(ltg-sl,2)
                data.append([my.lgpdm(gpdm),rq,ltg,sl,bl,sh,gs])

    except : 
        print("出错退出")
            
    return data
    
    

    
if __name__ == "__main__":  
#def temp():

#    sys.exit()

    socket.setdefaulttimeout(20)  # 设置socket层的超时时间为20秒
    
    now1 = datetime.datetime.now().strftime('%H:%M:%S')
    print('开始运行时间：%s' % now1)

    gpdmb=my.get_gpdm()
    
    #上市日期、行业、总股本、每股净资产
    gpssrq=my.get_stock_basics()
    
    gpdmb=gpdmb.join(gpssrq)
    
    #去掉还未上市的
    gpdmb=gpdmb.loc[(~(gpdmb['ssrq'].isna()) & (gpdmb['ssrq']<'20190501'))]
    
#    sys.exit()
    
    dbfn=my.getdrive()+'\\hyb\\DZH.db'
    dbcn = sqlite3.connect(dbfn)
    
    start_time = time.time()

    j=0
    
    for i in range(j,len(gpdmb)):
        gpdm=gpdmb.index[i]
        gpmc = gpdmb.iloc[i]['gpmc']
        print("共有%d只股票，正在处理第%d只：%s%s，请等待…………" % (len(gpdmb),i,gpdm,gpmc)) 
        data = get_gdhs(gpdm)
        
        if len(data)>0 :
            dbcn.executemany('INSERT OR REPLACE INTO GDHS (GPDM,RQ,GDHS) VALUES (?,?,?)', data)
            dbcn.commit()

        data = get_sdltgd(gpdm)
        
        if len(data)>0 :
            dbcn.executemany('''INSERT OR REPLACE INTO LTG (GPDM,RQ,LTG,SDGDCG,SDGDZB,SHCG,DGDGS)
            VALUES (?,?,?,?,?,?,?)''', data)

        if ((i+1) % 50 ==0) or i>=len(gpdmb)-1 :
            now_time = time.time()
            t1 = now_time - start_time
            #每只股票秒数            
            p = t1/(i-j)
            #估计剩余时间
            t1 = t1/60
            t2 = (len(gpdmb) - i)*p/60
            now = datetime.datetime.now().strftime('%H:%M:%S')
            
            print('------已用时%d分钟，估计还需要%d分钟(%s)' % (t1,t2,now))

            dbcn.commit()

    dbcn.close()


    now2 = datetime.datetime.now().strftime('%H:%M:%S')
    print('开始运行时间：%s' % now1)
    print('结束运行时间：%s' % now2)

'''
python使用pyquery库总结 
https://blog.csdn.net/baidu_21833433/article/details/70313839

'''

