# ---- File: pages/record_view.py ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import re
import matplotlib.pyplot as plt
import os
from yahooquery import Ticker


## ---------------------------------------------------------------------------------
##! -- functions 
## ---------------------------------------------------------------------------------

# def readTickerData(ticker):
#     temp_df = pd.read_csv(os.path.join(dir_ticker_price, ticker +'.AX_weekly.csv' ) )
#     temp_df = temp_df.iloc[:-1]
#     temp_df.index = pd.DatetimeIndex(temp_df.date)
#     temp_df.index.name = None
#     temp_df = temp_df[['adjclose']]
#     temp_df = temp_df.rename(columns = {'adjclose': ticker})
#     return(temp_df)

def readTickerData(tickers):
    tickers = [c+'.AX' for c in tickers]
    t = Ticker(tickers)
    end = datetime.today()
    start = end - timedelta(days=365)
    after_date = pd.to_datetime("01/01/" + str(datetime.now().year - 1) , dayfirst=True)
    # time.sleep(10)   # pause per iteration

    # # --- WEEKLY PRICE DATA --- #
    price_df = t.history(start=after_date.strftime("%Y-%m-%d"), # already defined as 01-01-YYYY
                     end=end.strftime("%Y-%m-%d"),
                     interval="1d")
    price_df = price_df.round(2)
    price_df = price_df.reset_index()
    price_df['date'] = pd.to_datetime(price_df['date'], format='mixed', utc=True)
    price_df['date'] = price_df['date'].dt.tz_localize(None)
    price_df['date']= price_df['date'].dt.strftime('%Y-%m-%d')
    price_df  = price_df.set_index(['date'])
    price_df.index.name = None
    price_df.index = pd.to_datetime(price_df.index)
    price_df = price_df.sort_index()
    ## -- merge
    price_df2 = pd.pivot(price_df, columns = ['symbol'], values=['adjclose'])
    price_df.columns.name = None
    price_df2.columns = price_df2.columns.get_level_values(1)
    price_df2.columns = [c.replace('.AX', '') for c in price_df2.columns ]
    return(price_df2)




## ---------------------------------------------------------------------------------
##! -- St page
## ---------------------------------------------------------------------------------
st.set_page_config(page_title="Record View", layout='wide')

if "df" not in st.session_state:
    st.error("Please go back and upload a file.")
    st.stop()

# if 'st.session_state.stocks' not in globals() :
#     st.session_state.stocks = ['WES']



watchlist = ['VTS', 'QUAL', 'VGS'] # NDQ MOAT has data from May 2015 onwards => affects charts



with st.sidebar:
    st.subheader('Select stocks for comparison:')
    stock_nav_selection = []
    for i in watchlist:
        res = st.checkbox(i, False)

    if st.button("Go"):
        st.session_state.stocks = stock_nav_selection
        st.rerun()
    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------

# col1, col2 = st.columns(2)

# with col1:
#! plot ticker price
if st.session_state.fetchLiveData:  
    ticker_data = readTickerData(st.session_state.stocks)
    ticker_data_norm = 100*(ticker_data/ticker_data.iloc[0] -1)
    # print(ticker_data/ticker_data.iloc[0])
    # st.dataframe(ticker_data.head())
    st.subheader('historic stock price (10 yr)')
    st.line_chart(ticker_data_norm, y_label='% return')
else:
    st.html('(Live data plot has been turned off)')

