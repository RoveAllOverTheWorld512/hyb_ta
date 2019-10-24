# -*- coding: utf-8 -*-
"""
Created on 2019-10-08 16:17:47

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

from datetime import datetime, timedelta
import matplotlib.dates as mpl_dt

matplotlib_epoch = datetime(1, 1, 1)  # utc
posix_epoch = datetime(1970, 1, 1)  # utc
DAY = 86400  # seconds


def plottm(u):
    """posix timestamp -> plot time"""
    td = (datetime.utcfromtimestamp(u) - matplotlib_epoch)
    return td.days + 1 + (1000000 * td.seconds + td.microseconds) / 1e6 / DAY


def unixtm(p):
    """plot time -> posix timestamp"""
    td = timedelta(days=p-1)
    return (matplotlib_epoch + td - posix_epoch).total_seconds()


f = datetime.utcfromtimestamp
u = 1270000000.1234567890
print(f(u))
print(mpl_dt.epoch2num(u))
print(plottm(u))
print(f(mpl_dt.num2epoch(mpl_dt.epoch2num(u))))
print(f(mpl_dt.num2epoch(plottm(u))))
print(f(unixtm(mpl_dt.epoch2num(u))))
print(f(unixtm(plottm(u))))

assert abs(mpl_dt.epoch2num(u) - plottm(u)) < 1e-5

p = 86401.234567890 / DAY
print(f(mpl_dt.num2epoch(p)))
print(f(unixtm(p)))
assert abs(mpl_dt.num2epoch(p) - unixtm(p)) < 1e-5

