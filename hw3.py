### home work 3
### market simulator


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

#def main(argv):



#this function takes in an array and retrieves all the data in columan:colindex
def retrieve(data,colindex):
    i = 0;
    size = len(data)
    col_data = [None]*size
    while i < size:
            '''retrieve data from data'''
            col_data[i] = data[i][colindex]
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

    #load order file
    path = r'C:\Users\Acer\Desktop\cs\data\orders.csv'
    na_data = np.loadtxt(path, delimiter=',', dtype='I4,I4,I4,S5,S5,f4')
    size = len(na_data)
    na_year = retrieve(na_data,0)
    na_month = retrieve(na_data,1)
    na_day = retrieve(na_data,2)
    na_symbols = retrieve(na_data,3)
    na_action = retrieve(na_data,4)
    na_shares = retrieve(na_data,5)

    #fetching adjusted closed
    ls_symbols = list(set(na_symbols))
    dt_start = dt.datetime(na_year[0],na_month[0], na_day[0])
    dt_end = dt.datetime(na_year[size-1],na_month[size-1], na_day[size-1]+1)
    dt_timeofday = dt.timedelta(hours=16)
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

    money = cash
    i = j = k = 0
    while i < len(ls_symbols):
        money = money - (position_array[0,i] * actual_close[0,i])
        i = i + 1
    i = 1
    while i < len(position_array):
        j = 0
        while j < len(ls_symbols):
            if (position_array[i,j] != position_array[i-1,j]):
                money = money - ((position_array[i,j]-position_array[i-1,j]) * actual_close[i,j])
                print 'change'
            portfolio_value[i][0] = portfolio_value[i][0] + (position_array[i,j] * actual_close[i,j])
            j= j + 1
        portfolio_value[i][0] = portfolio_value[i][0] + money
        portfolio_value[i][1] = ldt_timestamps[i].year
        portfolio_value[i][2] = ldt_timestamps[i].month
        portfolio_value[i][3] = ldt_timestamps[i].day
        
        i = i + 1
        
                
            
    
            

    return portfolio_value,position_array
#if __name__ == '__main__':
#    main(sys.argv)
