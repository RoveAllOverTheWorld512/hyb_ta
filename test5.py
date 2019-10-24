# -*- coding: utf-8 -*-
"""
Created on 2019-10-07 11:58:23

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import matplotlib
from numpy.random import randn
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
# 把y轴转化为百分比。
def to_percent(y, position):
    return str(100 * y) + '%'
# 直方图的数据集
x = randn(500)
# 设置直方图分组数量bins=60.
plt.hist(x, bins=60, weights= [1./ len(x)] * len(x))
formatter = FuncFormatter(to_percent)
plt.gca().yaxis.set_major_formatter(formatter)
plt.show()