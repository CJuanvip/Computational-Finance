#HWK 5

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import sys
import os
from collections import deque

#bollinger_bands takes in a symbol, start date, end_date and a numeric rolling back period
#the program returns the list of bollinger bands over this period
def bollinger_bands(symbol,dt_start, dt_end,rolling_period):
    #define dates, data source, retrieve actual close price
    dt_end = du.getNextNNYSEdays(dt_end,1,dt.timedelta(hours = 16))[0]
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end,dt.timedelta(hours=16))
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['actual_close','close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbol, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    actual_close = d_data['actual_close']

    #columbs: price, rolling average, rolling sttdev, bollinger_val
    bollinger_matrix = np.zeros((len(ldt_timestamps),4))
    rolling_prices = deque(np.zeros(rolling_period))

    #iterate through the actual
    for i in range(0, (len(ldt_timestamps))):
        bollinger_matrix[i,0] = actual_close[symbol[0]].ix[ldt_timestamps[i]]
        fx = rolling_prices.popleft()
        rolling_prices.append(bollinger_matrix[i,0])
        if (i < (rolling_period -1)): #no rolling average yet
            bollinger_matrix[i,1] = np.nan  #rolling avg
            bollinger_matrix[i,2] = np.nan  # rolling stddev
            bollinger_matrix[i,3] = np.nan  # bollinger_val
        else:
            bollinger_matrix[i,1] = np.average(rolling_prices)  #rolling avg
            print bollinger_matrix[i,1]
            bollinger_matrix[i,2] = np.std(rolling_prices)  # rolling stddev
            bollinger_matrix[i,3] = (bollinger_matrix[i,0] - bollinger_matrix[i,1])/bollinger_matrix[i,2] # bollinger_val: (price - rolling avg) / rolling stddev
    return bollinger_matrix, ldt_timestamps,actual_close

symbol = [('GOOG')]
start_date = dt.datetime(2010,12,1)
end_date = dt.datetime(2010,12,30)
rolling = 20
a,b,c = bollinger_bands(symbol,start_date,end_date,rolling)
