##HWK 4
'''
This program takes in a list of symbols
generate the events into a list of trade list
finally the marketsim function takes in the list and calculates the performance

'''

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


#find_events takes in a list of symbols:ls_symbols, the pricing data enclosed in a dict:d_data
def find_event(ls_symbols, d_data):
    df_close = d_data['actual_close']
    #ts_market = df_close['SPY']

    print "Finding Events"
    trade_count = 0
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]

            #this is the event
            if f_symprice_today < 10.0 and f_symprice_yest >= 10: 
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                trade_count = trade_count + 1

    return df_events, trade_count

##trade generator takes in 
def trade_generator(start_date,end_date):
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list("sp5002012")
    #ls_symbols.append('SPY')
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))
    ls_keys = ['actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events,trade_count = find_event(ls_symbols,d_data)

    # generate trade list from events
    trade_list = (2011, 1, 14, 'AAPL', 'Buy', 1500.0)
    trade_list = np.array(trade_list,dtype='I4,I4,I4,S5,S5,f4')
    time_size = len(ldt_timestamps)
    for i in range(1, time_size):
        for s_sym in ls_symbols:
            if (df_events[s_sym].ix[ldt_timestamps[i]] == 1):
                temp_trade = (ldt_timestamps[i].year,ldt_timestamps[i].month,ldt_timestamps[i].day,s_sym,'Buy',100.0)
                temp_trade = np.array(temp_trade,dtype='I4,I4,I4,S5,S5,f4')
                trade_list = np.vstack((trade_list,temp_trade))
                if (i + 5 < time_size):
                    temp_trade = (ldt_timestamps[(i+5)].year,ldt_timestamps[(i+5)].month,ldt_timestamps[(i+5)].day,s_sym,'Sell',100.0)
                else:
                    temp_trade = (ldt_timestamps[(time_size-1)].year,ldt_timestamps[(time_size-1)].month,ldt_timestamps[(time_size-1)].day,s_sym,'Sell',100.0)
                temp_trade = np.array(temp_trade,dtype='I4,I4,I4,S5,S5,f4')
                trade_list = np.vstack((trade_list,temp_trade))
    return trade_list[1:]

def retrieve(data,colindex):
    i = 0;
    size = len(data)
    col_data = [None]*size
    while i < size:
            '''retrieve data from data'''
            col_data[i] = data[i][0][colindex]
            i = i + 1

    return col_data                

def mark(cash):
        #print 'Number of arguments:', len(sys.argv), 'arguments.'
        #print 'Argument List:', str(sys.argv)
    starting_cash = cash  #= sys.argv[1]
    order_file = 'orders.csv'  #sys.argv[2]
    value_file = 'values.csv' #sys.argv[3]
    #retrieve data from yahoo
    '''path = r'C:\Users\Acer\Desktop\cs\data\orders2.csv'
    order_file_path = r(path + order_file)'''
    #value_file_path = os.path.abspath(os.path.join(path, value_file))
    dt_start = dt.datetime(2008,1,1)
    dt_end = dt.datetime(2009,12,31)
    dt_timeofday = dt.timedelta(hours=16)

    #load order file
    path = r'C:\Users\Acer\Desktop\cs\data\orders.csv'
    #na_data = np.loadtxt(path, delimiter=',', dtype='I4,I4,I4,S5,S5,f4')
    na_data = trade_generator(dt_start,dt_end)
    size = len(na_data)
    na_year = retrieve(na_data,0)
    na_month = retrieve(na_data,1)
    na_day = retrieve(na_data,2)
    na_symbols = retrieve(na_data,3)
    na_action = retrieve(na_data,4)
    na_shares = retrieve(na_data,5)

    #fetching adjusted closed
    ls_symbols = list(set(na_symbols))
    #dt.datetime(na_year[0],na_month[0], na_day[0])
    #dt.datetime(na_year[size-1],na_month[size-1], na_day[size-1]+1)
    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end,dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    actual_close = d_data['actual_close'].values

    #position
    position_array = np.zeros(((len(actual_close)),(len(ls_symbols))))
   
    #calculate the holding of each share everyday
    i = j = k = 0

    while k < len(na_action):
        j = 0
        while j < len(ls_symbols):
            i = 0
            if(ls_symbols[j] == na_symbols[k]):
                while i < len(ldt_timestamps):
                    if ( (ldt_timestamps[i].year == na_year[k]) & (ldt_timestamps[i].month == na_month[k]) & (ldt_timestamps[i].day == na_day[k])):
                        action =    1
                        if ( na_action[k] == 'Sell'):
                            action = -1
                        position_array[i,j] = position_array[i,j] + action* na_shares[k]
                    i = i + 1
            j = j + 1
        k = k + 1
       
    #cumulative position
    i = j = k = 0
    while k < len(ls_symbols):
        i = 1
        while i < len(position_array):
            position_array[i,k] = position_array[i-1,k] + position_array[i,k]
            i = i + 1
        k = k + 1

    #portfolio value position
    portfolio_value = np.zeros(((len (position_array)),4))
    portfolio_value[0][0] = cash
    daily_return = np.zeros(len(position_array))

    money = cash
    i = j = k = 0
    while i < len(ls_symbols):
        money = money - (position_array[0,i] * actual_close[0,i])
        i = i + 1
    i = 1
    while i < len(ldt_timestamps):
        j = 0
        while j < len(ls_symbols):
            if (i < len(position_array)):
                if (position_array[i,j] != position_array[i-1,j]):
                    money = money - ((position_array[i,j]-position_array[i-1,j]) * actual_close[i,j])
                    #print 'change'
                portfolio_value[i][0] = portfolio_value[i][0] + (position_array[i,j] * actual_close[i,j])
                j= j + 1
        portfolio_value[i][0] = portfolio_value[i][0] + money
        portfolio_value[i][1] = ldt_timestamps[i].year
        portfolio_value[i][2] = ldt_timestamps[i].month
        portfolio_value[i][3] = ldt_timestamps[i].day

        daily_return[i] = (portfolio_value[i][0]/portfolio_value[(i-1)][0])-1
        i = i + 1
        
                
            
    
    port_std = np.std(daily_return)
    port_ret = sum(daily_return)
    average_daily_return = np.mean(daily_return)
    sharp_ratio = math.sqrt(250) * average_daily_return / port_std

    return portfolio_value,daily_return , sharp_ratio              


#dt_start = dt.datetime(2008, 1, 1)    
#dt_end = dt.datetime(2009, 12, 31)

#ja,tc = trade_generator(dt_start,dt_end)
#ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
#trade_list = (2011, 1, 14, 'AAPL', 'Buy', 1500.0)
#trade_list = np.array(trade_list,dtype='I4,I4,I4,S5,S5,f4')
#temp_trade = (ldt_timestamps[i].year,ldt_timestamps[i].month,ldt_timestamps[i].day,'AMD','Buy',100.0)
#temp_trade = np.array(temp_trade,dtype='I4,I4,I4,S5,S5,f4')
#np.vstack((trade_list,temp_trade))
