import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math 


def stimulate(s_date, e_date, ls_symbols, s_allocations): #
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(s_date, e_date, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    na_price,open_price,actual_close = d_data['close'].values,d_data['open'].values,d_data['actual_close'].values
    na_price_previous = na_price[0:len(na_price)-1]
    na_price_previous = np.vstack((na_price_previous[0],na_price_previous))

    daily_return = (na_price / na_price_previous)-1
    #daily_return = (actual_close / open_price) - 1
    #daily_return = (actual_close / na_price_previous) - 1
    daily_return = daily_return * s_allocations
    port_daily_reutrn = daily_return.sum(axis = 1)
    average_daily_return = np.average(port_daily_reutrn)
    
    cum_return = sum(((na_price[len(na_price)-1] / na_price[0]) - 1 ) * s_allocations)# day N price / day 0 price - 1
    

    port_std = np.std(port_daily_reutrn)
    sharp_ratio = math.sqrt(250) * average_daily_return / port_std
    
    
    #na_s_price = d_data['open'].values
    
    return sharp_ratio
    #return daily_return, port_std, average_daily_return, sharp_ratio

def optimize(s_date, e_date, ls_symbols):
    allocations = np.zeros(len(ls_symbols))
    optimal_allocations = allocations
    optimal_allocations[len(optimal_allocations)-1] = 1
    optimal_sharp_ratio = stimulate(s_date, e_date, ls_symbols, optimal_allocations)
    curr_sr = 0;
    a,b,c,d = 10,0,0,0
    while a >= 0:
        #print [a,b,c,d]
        b = max(0,10 - a)
        while b >= 0:
            c = max(0,10 - a - b)
            #print [a,b,c,d]
            while c >= 0:
                d = max(0, 10 - a - b - c) 
                #print [a,b,c,d]
                while d >= 0 :
                    if (a+b+c+d != 10): break
                    curr_sr = stimulate(s_date, e_date, ls_symbols,[a,b,c,d])
                    if (curr_sr > optimal_sharp_ratio):
                        optimal_sharp_ratio = curr_sr
                        optimal_allocations = [a,b,c,d]
                    #if (a+b+c == 10): break
                    print [a,b,c,d]
                    d = d - 1
                    
                #if (a+b == 10): break
                c = c - 1
                
            #if (b == 10): break
            b = b - 1
            
        a = a - 1
    return optimal_sharp_ratio, optimal_allocations               
                
                                        
ls_symbols = ['BRCM', 'TXN', 'AMD', 'ADI'] 
dt_start = dt.datetime(2011, 1, 1)
dt_end = dt.datetime(2011, 12, 31)
s_allocations = [0.4,0.4,0.0,0.2]

#ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
#dt_start = dt.datetime(2010, 1, 1)
#dt_end = dt.datetime(2010, 12, 31)
#s_allocations = [0,0,0,1]


#sr = stimulate(dt_start, dt_end, ls_symbols, s_allocations)
sr,ac = optimize(dt_start,dt_end,ls_symbols)
