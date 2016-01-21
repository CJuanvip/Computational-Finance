"""
Home work 2 for computational investing
"""

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_event(ls_symbols, d_data):
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            '''f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol went down below $5'''
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            
            if f_symprice_today < 5.0 and f_symprice_yest >= 5:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events



dataobj = da.DataAccess('Yahoo')
symbols = dataobj.get_symbols_from_list("sp5002008")
symbols.append('SPY')

symbols2 = dataobj.get_symbols_from_list("sp5002012")
symbols2.append('SPY')

dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

#dataobj = da.DataAccess('Yahoo')
#ls_symbols = dataobj.get_symbols_from_list('sp5002012')
#ls_symbols.append('SPY')

ls_keys = ['actual_close','close']
ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

df_events = find_event(symbols, d_data)
print "Creating Study"
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='Q1a.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')




ldf_data = dataobj.get_data(ldt_timestamps, symbols2, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

df_events = find_event(symbols2, d_data)
print "Creating Study"
ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='Q1b.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
