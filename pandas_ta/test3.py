# -*- coding: utf-8 -*-
"""
Created on 2019-10-06 20:41:34

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from stock_pandas.tdx.tdxdayread import Tdxday
from stock_pandas.tdx.tdxcfg import Tdx
from stock_pandas.tdx.class_func import *
import pandas_ta as ta


filename = '600138'
tdxday = Tdxday(filename)
df = tdxday.get_qfqdata()
rng_date = df.index
df = df.reset_index()