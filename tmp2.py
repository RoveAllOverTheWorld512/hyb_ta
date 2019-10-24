# -*- coding: utf-8 -*-
"""
Created on 2019-10-08 12:09:45

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd

df=pd.DataFrame({'f_num': [1.,2.,3.], 'i_num':[1,2,3], 
                 'char': ['a','bb','ccc'], 'mixed':['a','bb',1]})

struct_arr=df.to_records(index=False)

print('struct_arr',struct_arr.dtype,'\n')