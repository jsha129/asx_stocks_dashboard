# ---- File: pages/record_view.py ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import re
import matplotlib.pyplot as plt
import os
from yahooquery import Ticker
import seaborn as sns

st.set_page_config(layout="wide") 
#!! Fetch stock price from internet instead of presaved files

# ticker_price_avail = sorted([ c.replace('.AX_weekly.csv','')  for c in os.listdir(dir_ticker_price)])
## ---------------------------------------------------------------------------------
##! -- functions 
## ---------------------------------------------------------------------------------

dir_ticker_price = '/home/jay/Documents/python_stock_market/2024_July/yahooquery_more_data/data/prices/'
def readTickerData_offline(ticker):
    '''Read data from dir with saved data'''
    temp_df = pd.read_csv(os.path.join(dir_ticker_price, ticker +'.AX_weekly.csv' ) )
    temp_df = temp_df.iloc[:-1]
    temp_df.index = pd.DatetimeIndex(temp_df.date)
    temp_df.index.name = None
    temp_df = temp_df[['adjclose']]
    temp_df = temp_df.rename(columns = {'adjclose': ticker})
    return(temp_df)

def readTickerData_live(tickers):
    tickers = [c+'.AX' for c in tickers]
    t = Ticker(tickers)
    end = datetime.today()
    start = end - timedelta(days=365*10)
    after_date = pd.to_datetime("01/01/" + str(datetime.now().year - 10) , dayfirst=True)
    # time.sleep(10)   # pause per iteration

    # # --- WEEKLY PRICE DATA --- #
    price_df = t.history(start=after_date.strftime("%Y-%m-%d"), # already defined as 01-01-YYYY
                     end=end.strftime("%Y-%m-%d"),
                     interval="1wk")
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

    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------

#! plot ticker price
stock_nav_selection = st.session_state.stocks
fetchLiveData = st.checkbox('Fetch data from internet?', value = False)

if not fetchLiveData:
    # st.html('Using existing data:')
    if os.path.isdir(dir_ticker_price):
        st.success('Yay! Downloaded data exists')
        # st.html(stock_nav_selection)
        ticker_data = readTickerData_offline('VAS')
        for i in st.session_state.stocks:
            temp_df = readTickerData_offline(i)
            ticker_data = pd.concat([ticker_data, temp_df], axis = 1)
        ticker_data_norm = 100*(ticker_data/ticker_data.iloc[0] -1) 
    else:
        st.error('Directory with downloaded data not found. Try "Fetcing data from internet"')
else:
    if fetchLiveData:
        st.session_state.stocks.append('VAS')    
        ticker_data = readTickerData_live(stock_nav_selection)
        ticker_data_norm = 100*(ticker_data/ticker_data.iloc[0] -1)
        # print(ticker_data/ticker_data.iloc[0])
        # st.dataframe(ticker_data.head())
        st.subheader(stock_nav_selection[0]+ ' historic stock price (10 yr)')
        # st.line_chart(ticker_data_norm, y_label='% return')
    else:
        st.html('(Live data plot has been turned off)')

if 'ticker_data_norm' in globals():
    fig, ax = plt.subplots(figsize=(8,6))  
    sns.lineplot(data = ticker_data_norm)
    ax.set_title("Weekly stock price over last 10 years")
    ax.set_xlabel("Date")
    ax.set_ylabel("% return")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    with st.container(width=600): 
        st.pyplot(fig, width = 'content')    
else:
    st.error('Something went wrong! Try again later.')  
