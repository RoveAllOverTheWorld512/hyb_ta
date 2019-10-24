# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 12:07:29 2018

@author: lenovo
"""

import tushare as ts  
import datetime  
 
#从TuShare读取开市日历，然后自己计算week/month/querter/year sart/end 属性
#然后保存在本地以供以后使用

mytoken='18fcea168f6c1f8621c13bef376e726cf5e31fde3f579db37929181b'
pro = ts.pro_api(token=mytoken)

cal_dates=pro.trade_cal(start_date='19901219',end_date='20180505',fields='cal_date,is_open,pretrade_date')
cal_dates=cal_dates.append(pro.trade_cal(start_date='20180506',end_date='20191231',fields='cal_date,is_open,pretrade_date'))
cal_dates=cal_dates.sort_values(by='cal_date')
cal_dates=cal_dates.reset_index()
cal_dates=cal_dates[['cal_date','is_open','pretrade_date']]
cal_dates.columns=['calendarDate', 'isOpen','pretrade_date']

cal_dates['isWeekStart'] = 0
cal_dates['isWeekEnd'] = 0
cal_dates['isMonthStart'] = 0
cal_dates['isMonthEnd'] = 0
cal_dates['isQuarterStart'] = 0
cal_dates['isQuarterEnd'] = 0
cal_dates['isYearStart'] = 0
cal_dates['isYearEnd'] = 0

previous_i = -1
previous_open_week = -1
previous_open_month = -1
previous_open_year = -1
 
for i in cal_dates.index:
    
    str_date = cal_dates.loc[i]['calendarDate']
    isOpen = cal_dates.loc[i]['isOpen']
    
    if not isOpen:
        continue
    
    date = datetime.datetime.strptime(str_date, '%Y%m%d').date()
    
    #设置isWeekStart和isWeekEnd
    current_open_week = date.isocalendar()[1]
    if current_open_week != previous_open_week:
        cal_dates.loc[i, 'isWeekStart'] = 1
        if previous_open_week != -1:
            cal_dates.loc[previous_i, 'isWeekEnd'] = 1
        
    #设置isMonthStart和isMonthEnd
    current_open_month = date.month
    if current_open_month != previous_open_month:
        cal_dates.loc[i, 'isMonthStart'] = 1
        if previous_open_month != -1:
            cal_dates.loc[previous_i, 'isMonthEnd'] = 1
        #顺便根据月份设置isQuarterStart和isQuarterEnd
        if current_open_month in [1, 4, 7, 10]:
            cal_dates.loc[i, 'isQuarterStart'] = 1 
            if previous_open_month != -1:
                cal_dates.loc[previous_i, 'isQuarterEnd'] = 1
        #有个特殊情况是交易所开始第一天应为QuarterStart
        if previous_open_month == -1:
            cal_dates.loc[i, 'isQuarterStart'] = 1
            
    #设置isYearStart和isYearEnd
    current_open_year = date.year
    #当前年份不等于前一年份
    if current_open_year != previous_open_year:
        cal_dates.loc[i, 'isYearStart'] = 1
        if previous_open_year != -1:
            cal_dates.loc[previous_i, 'isYearEnd'] = 1   
 
    previous_i = i
    previous_open_week = current_open_week
    previous_open_month = current_open_month
    previous_open_year = current_open_year
    
#保证标注最后一年的isYearEnd
if cal_dates.loc[i]['calendarDate'][4:]=='1231':
    if cal_dates.loc[i]['isOpen'] == 1:
        cal_dates.loc[i,'isYearEnd'] = 1
    else:
        pretradedate=cal_dates.loc[i]['pretrade_date']
        cal_dates.loc[cal_dates['calendarDate']==pretradedate,'isYearEnd'] = 1
        
        
    
cal_dates.to_csv(r'd:\selestock\calAll.csv',index=False)
