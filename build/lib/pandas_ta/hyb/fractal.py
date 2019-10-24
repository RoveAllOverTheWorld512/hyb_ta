# -*- coding: utf-8 -*-
"""
Created on 2019-09-26 18:15:24

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from pandas import date_range, DataFrame, RangeIndex, Timedelta
from ..utils import get_offset, verify_series

def fractal(high, low, offset=None, **kwargs):
    """
    Indicator: fractal
    
    """
    high = verify_series(high)
    low = verify_series(low)
    offset = get_offset(offset)
    

    # Calculate Result
    h_1 = (high.diff(1)>0).astype(int)    #ÓëÇ°Ò»Ìì±È½Ï£¬¸ßÓÚÇ°Ò»ÌìÎª1
    h_2 = (high.diff(2)>0).astype(int)    #ÓëÇ°Á½Ìì±È½Ï£¬¸ßÓÚÇ°Á½ÌìÎª1

    h1 = (high.diff(-1)>=0).astype(int)    #ÓëºóÒ»Ìì±È½Ï£¬¸ßÓÚ»òµÈÓÚºóÒ»ÌìÎª1
    h2 = (high.diff(-2)>=0).astype(int)    #ÓëºóÁ½Ìì±È½Ï£¬¸ßÓÚ»òµÈÓÚºóÇ°Á½ÌìÎª1

    fractal_up = ((h_1 + h_2 + h1 + h2)==4).astype(int) 
    fractal_up.name = 'FRACTAL_UP'
    fractal_upvalue = high * fractal_up    
    fractal_upvalue.name = 'FRACTAL_UPPRICE'

    l_1 = (low.diff(1)<0).astype(int)    #ÓëÇ°Ò»Ìì±È½Ï£¬µÍÓÚÇ°Ò»ÌìÎª1
    l_2 = (low.diff(2)<0).astype(int)    #ÓëÇ°Á½Ìì±È½Ï£¬µÍÓÚÇ°Á½ÌìÎª1

    l1 = (low.diff(-1)<=0).astype(int)    #ÓëºóÒ»Ìì±È½Ï£¬µÍÓÚ»òµÈÓÚºóÒ»ÌìÎª1
    l2 = (low.diff(-2)<=0).astype(int)    #ÓëºóÁ½Ìì±È½Ï£¬µÍÓÚ»òµÈÓÚºóÇ°Á½ÌìÎª1

    fractal_down = ((l_1 + l_2 + l1 + l2)==4).astype(int) 
    fractal_down.name = 'FRACTAL_DOWN'
    fractal_downvalue = low * fractal_down    
    fractal_downvalue.name = 'FRACTAL_DOWNPRICE'

    # Prepare ractal DataFrame
    data = {fractal_up.name: fractal_up, fractal_upvalue.name: fractal_upvalue,  \
            fractal_down.name:fractal_down, fractal_downvalue.name:fractal_downvalue}
    fractaldf = DataFrame(data)
    
#    fractaldf = fractaldf.replace(0,np.NaN)
    
    fractaldf.category = 'hyb_ta'

    return fractaldf



fractal.__doc__ = \
"""
·ÖÐÎ

"""

