# -*- coding: utf-8 -*-
"""
Created on 2019-10-07 10:59:12

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(np.arange(2000, 2010), range(10))
ax.get_xaxis().get_major_formatter().set_useOffset(False)
