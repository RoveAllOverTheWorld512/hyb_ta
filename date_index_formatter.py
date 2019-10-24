"""
=====================================
Custom tick formatter for time series
=====================================

When plotting time series, e.g., financial time series, one often wants
to leave out days on which there is no data, i.e. weekends.  The example
below shows how to use an 'index formatter' to achieve the desired plot
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker

# Load a numpy record array from yahoo csv data with fields date, open, close,
# volume, adj_close from the mpl-data/example directory. The record array
# stores the date as an np.datetime64 with a day unit ('D') in the date column.
# np.load()
with cbook.get_sample_data('goog.npz') as datafile:
    r = np.load(datafile)['price_data'].view(np.recarray)


#with cbook.get_sample_data('goog.npz') as datafile:
#    r0= np.load(datafile)   
#    # type(r0) --> numpy.lib.npyio.NpzFile
#    # r0.files --> ['price_data']
#    r1 = r0['price_data']
#    # type(r1) --> numpy.ndarray
#    r = r1.view(np.recarray)
#    # type(r) -- > numpy.recarray

r = r[-30:]  # get the last 30 days
# Matplotlib works better with datetime.datetime than np.datetime64, but the
# latter is more portable.
# r.dtype
# dtype((numpy.record, [('date', '<M8[D]'), ('open', '<f8'), ('high', '<f8'),
# ('low', '<f8'), ('close', '<f8'), ('volume', '<i8'), ('adj_close', '<f8')]))

date = r.date.astype('O')  #变成了Object类型

# first we'll do it the default way, with gaps on weekends
fig, axes = plt.subplots(ncols=2, figsize=(8, 4))
ax = axes[0]
ax.plot(date, r.adj_close, 'o-')
ax.set_title("Default")
fig.autofmt_xdate()

# next we'll write a custom formatter
N = len(r)
ind = np.arange(N)  # the evenly spaced plot indices等距绘图索引


def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, N - 1)
    # np.clip()修剪 这个函数可以控制thisind在0到N-1的整数
    #避免date[thisind]出界，抛出
    #IndexError: index 30 is out of bounds for axis 0 with size 30
    # x=np.array([1,2,3,5,6,7,8,9])
    # np.clip(x,3,8)  结果：array([3, 3, 3, 5, 6, 7, 8, 8])
    return date[thisind].strftime('%Y-%m-%d')

ax = axes[1]
ax.plot(ind, r.adj_close, 'o-')
fmt = ticker.FuncFormatter(format_date)
ax.xaxis.set_major_formatter(fmt)
ax.set_title("Custom tick formatter")
fig.autofmt_xdate()

plt.show()
