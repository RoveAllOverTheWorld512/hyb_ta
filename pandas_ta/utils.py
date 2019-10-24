# -*- coding: utf-8 -*-
import math
import numpy as np
import pandas as pd

from functools import reduce
from operator import mul
from sys import float_info as sflt

TRADING_DAYS_IN_YEAR = 250
TRADING_HOURS_IN_DAY = 6.5
MINUTES_IN_HOUR = 60

def combination(**kwargs):
    """https://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
    排列组合计算
    """
    n = int(math.fabs(kwargs.pop('n', 1)))
    r = int(math.fabs(kwargs.pop('r', 0)))

    if kwargs.pop('repetition', False) or kwargs.pop('multichoose', False):
        n = n + r - 1

    # if r < 0: return None
    r = min(n, n - r)
    if r == 0:
        return 1

    numerator   = reduce(mul, range(n, n - r, -1), 1)
    denominator = reduce(mul, range(1, r + 1), 1)
    return numerator // denominator


def cross(series_a:pd.Series, series_b:pd.Series, above:bool =True, asint:bool =True, offset:int =None, **kwargs):
    '''
    两个Pandas Series交叉,series_a向上穿过series_b
    '''
    series_a = verify_series(series_a)
    series_b = verify_series(series_b)
    offset = get_offset(offset)

    series_a.apply(zero)
    series_b.apply(zero)

    # Calculate Result
    current = series_a > series_b   # current is above
    previous = series_a.shift(1) < series_b.shift(1) # previous is below
    
    # above if both are true, below if both are false
    cross = current & previous if above else ~current & ~previous
    
    if asint:
        cross = cross.astype(int)

    # Offset
    if offset != 0:
        cross = cross.shift(offset)

    # Name & Category
    cross.name = f"{series_a.name}_{'XA' if above else 'XB'}_{series_b.name}"
    cross.category = 'utility'

    #返回的是一个pd.Series
    return cross


def df_error_analysis(dfA:pd.DataFrame, dfB:pd.DataFrame, **kwargs):
    """ 
    两个DataFrame的偏差分析,注意：两个DataFrame的列和索引应该一致
    调用案例：df_error_analysis(dfA,dfB,col=['open'])
    """
    col = kwargs.pop('col', None)
    #皮尔森相关系数
    corr_method = kwargs.pop('corr_method', 'pearson')

    # Find their differences
    diff = dfA - dfB

    df = diff.describe()
    #均方差、平均绝对偏差、平均值的无偏标准误差、皮尔森相关系数
    extra = pd.DataFrame([diff.var(), diff.mad(), diff.sem(), dfA.corrwith(dfB, method=corr_method)], index=['var', 'mad', 'sem', 'corr'])

    # Append the differences to the DataFrame
    df = df.append(extra)

    if col is not None:
        return df[col]
    else:
        return df

def fibonacci(**kwargs):
    """Fibonacci Sequence as a numpy array
    以Numpy数组输出斐波那契数列
    参数：n=10,zero=False,weighted=False
    zerob=True，表示从0开始，0、1、1、2、3……
    weighted=True,表示输出为权重（占比值），各值占总和之比，
    
    """
    n = int(math.fabs(kwargs.pop('n', 2)))
    zero = kwargs.pop('zero', False)
    weighted = kwargs.pop('weighted', False)

    if zero:
        a, b = 0, 1
    else:
        n -= 1
        a, b = 1, 1

    result = np.array([a])
    for i in range(0, n):
        a, b = b, a + b
        result = np.append(result, a)

    if weighted:
        fib_sum = np.sum(result)
        if fib_sum > 0:
            return result / fib_sum
        else:
            return result
    else:
        return result


def get_drift(x:int):
    """Returns an int if not zero, otherwise defaults to one.
    返回非0整数，否则默认1
    """
    return int(x) if x and x != 0 else 1


def get_offset(x:int):
    """Returns an int, otherwise defaults to zero.
    返回一整数，否则默认0
    """
    return int(x) if x else 0


def pascals_triangle(n:int =None, **kwargs):
    """Pascal's Triangle
    杨辉三角
    weighted=True,表示输出为权重（占比值），各值占总和之比
    inverse weighted=True,表示逆权重（1-权重）
    
    Returns a numpy array of the nth row of Pascal's Triangle.
    n=4  => triangle: [1, 4, 6, 4, 1]
         => weighted: [0.0625, 0.25, 0.375, 0.25, 0.0625
         => inverse weighted: [0.9375, 0.75, 0.625, 0.75, 0.9375]
    """
    n = int(math.fabs(n)) if n is not None else 0
    weighted = kwargs.pop('weighted', False)
    inverse = kwargs.pop('inverse', False)

    # Calculation
    triangle = np.array([combination(n=n, r=i) for i in range(0, n + 1)])
    triangle_sum = np.sum(triangle)
    triangle_weights = triangle / triangle_sum
    inverse_weights = 1 - triangle_weights

    if weighted and inverse:
        return inverse_weights
    if weighted:
        return triangle_weights
    if inverse:
        return None

    return triangle


def signed_series(series:pd.Series, initial:int =None):
    """Returns a Signed Series with or without an initial value
    返回带或不带初始值的带符号序列
    """
    series = verify_series(series)
    sign = series.diff(1)  #一阶差分，即与前一之差
    sign[sign > 0] = 1
    sign[sign < 0] = -1
    sign.iloc[0] = initial
    return sign


def symmetric_triangle(n:int =None, **kwargs):
    '''
    参数weighted=True,返回
    '''
    n = int(math.fabs(n)) if n is not None else 2
    weighted = kwargs.pop('weighted', False)

    if n == 2:
        triangle = [1, 1]
    
    if n > 2:
        if n % 2 == 0:
            front = [i + 1 for i in range(0, math.floor(n/2))]
            triangle = front + front[::-1]
        else:
            front = [i + 1 for i in range(0, math.floor(0.5 * (n + 1)))]
            triangle = front.copy()
            front.pop()
            triangle += front[::-1]

    if weighted:
        triangle_sum = np.sum(triangle)
        triangle_weights = triangle / triangle_sum
        return triangle_weights
    
    return triangle


def verify_series(series:pd.Series):
    """
    确定series为Pandas Series类型
    """
    if series is not None and isinstance(series, pd.core.series.Series):
        return series


def weights(w):
    def _dot(x):
        return np.dot(w, x)
    return _dot


def zero(x):
    """
    如果该值接近零，则返回零。否则返回值。
    """
    return 0 if -sflt.epsilon < x and x < sflt.epsilon else x


if __name__ == "__main__":
#    nCr=combination(n=5,r=2)
#    print(nCr)
    
#    print(get_offset(-12.5))
    
    import pandas as pd
    
#    df = pd.read_csv(r'F:\pandas-ta\data\sample.csv',index_col='date', parse_dates=True)
#    df.index=pd.to_datetime(df.index)
#    df=df.drop(columns='Unnamed: 0')
    
    
#    df = pd.read_csv(r'F:\pandas_hybta\data\002294.csv',index_col='date', parse_dates=True)
#    df.index=pd.to_datetime(df.index)
#
#    series_a=df['open']
#    series_b=df['close']
#    
#    jc1=cross(series_a, series_b)
#    jc2=cross(series_b, series_a)
#    
#    df['o_c']=jc1
#    df['c_o']=jc2
#    
#    df=df.drop(columns=['high','low'])
#    df.to_csv('cross.csv')
    
#    dfA = pd.read_csv(r'F:\pandas_hybta\data\002294_1.csv',index_col='date', parse_dates=True)
#    dfA.index=pd.to_datetime(dfA.index)
#    
#    dfB = pd.read_csv(r'F:\pandas_hybta\data\002294_2.csv',index_col='date', parse_dates=True)
#    dfB.index=pd.to_datetime(dfB.index)
#    
#    print(df_error_analysis(dfA,dfB,col=['open','high']))
    
#    na=fibonacci(n=10, weighted=True)
    
#    df = pd.read_csv(r'F:\pandas_hybta\data\002294_1.csv',index_col='date', parse_dates=True)
    df = pd.read_csv(r'F:\pandas_hybta\data\600674.csv',index_col='date', parse_dates=True)
    