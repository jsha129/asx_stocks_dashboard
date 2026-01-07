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

# if 'st.session_state.stocks' not in globals() :
#     st.session_state.stocks = ['WES']


df = st.session_state.df
df_cagr = st.session_state.df_cagr
# st.session_state.selected_index = []
# st.session_state.stocks = ['CBA']
default_stock_indices = ['VTS', 'QUAL', 'VGS'] # NDQ MOAT has data from May 2015 onwards => affects charts

# record = df.iloc[idx]

dir_ticker_price = '/home/jay/Documents/python_stock_market/2024_July/yahooquery_more_data/data/prices/'
# ticker_price_avail = sorted([ c.replace('.AX_weekly.csv','')  for c in os.listdir(dir_ticker_price)])
# ticker_price_avail = df['Code'][:10,].to_list()
ticker_price_avail = set(df_cagr['Code'].to_list()).intersection( set(st.session_state.df_avg_fund.index) ).intersection( set(st.session_state.df_raw_fund.index ) )
ticker_price_avail = sorted(ticker_price_avail)

# with st.sidebar:
#     st.html('Data available on stocks: '+ str(len(ticker_price_avail)))
#     stock_nav_selection = [st.selectbox('Jump to ASX stock: ', ticker_price_avail)]
#     st.html('<b>Choose Reference Indices:')
#     select_indices = []
#     for i in default_stock_indices:
#         temp_ref_index = st.checkbox(label = i)
#         if temp_ref_index: 
#             stock_nav_selection.append(i)
#     if st.button("Go"):
#         st.session_state.stocks = stock_nav_selection
#         st.rerun()
    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------

# col1, col2 = st.columns(2)

# with col1:
st.subheader('Note: Turn off live data in the Home page if error appears here.')
#! plot ticker price
if st.session_state.fetchLiveData:
    st.session_state.stocks.append('VAS')    
    ticker_data = readTickerData(st.session_state.stocks)
    ticker_data_norm = 100*(ticker_data/ticker_data.iloc[0] -1)
    # print(ticker_data/ticker_data.iloc[0])
    # st.dataframe(ticker_data.head())
    st.subheader(stock_nav_selection[0]+ ' historic stock price (10 yr)')
    st.line_chart(ticker_data_norm, y_label='% return')
else:
    st.html('(Live data plot has been turned off)')
## -- stock stats
st.html('<b>Stock Performance (2015 - 2025) </b>')
st.html('(Note: data has been precalculated offline)')
if stock_nav_selection[0] in list(df_cagr['Code']):
    temp = df_cagr[ df_cagr['Code'] == stock_nav_selection[0] ][ ['Code', 'Sector','annual_growth_percent','r_squared', 'n', 'freq'] ]
    st.html('<b>Code: </b>' + str(temp.iloc[0,0]))
    st.html('<b>Sector: </b>' + str(temp.iloc[0,1]))
    st.html('<b>Annual growth rate, CAGR: </b>' + str(temp.iloc[0,2]) + '%')
    st.html('<b>R-sqaured of the fit: </b>' + str(temp.iloc[0,3]))
    st.html('<b>Number of Weeks data: </b>' + str(temp.iloc[0,4]))
    # st.dataframe(temp.T)
    # del temp
else:
    st.html('Data not available')

