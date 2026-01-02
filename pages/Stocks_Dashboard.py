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

with st.sidebar:
    st.html('Data available on stocks: '+ str(len(ticker_price_avail)))
    stock_nav_selection = [st.selectbox('Jump to ASX stock: ', ticker_price_avail)]
    st.html('<b>Choose Reference Indices:')
    select_indices = []
    for i in default_stock_indices:
        temp_ref_index = st.checkbox(label = i)
        if temp_ref_index: 
            stock_nav_selection.append(i)
    if st.button("Go"):
        st.session_state.stocks = stock_nav_selection
        st.rerun()
    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
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

with col2:
    ##! Fundamental dats
    #! avg fundamental ratio
    if stock_nav_selection[0] in list(st.session_state.df_avg_fund.index):    
        temp_fund_avg = st.session_state.df_avg_fund.loc[stock_nav_selection[0] ]
        temp_fund_avg = temp_fund_avg.to_dict()
        st.subheader('{} year average of key ratio'.format(str(int(temp_fund_avg['n']))))
        temp_fund_avg_key_order = ['ROIC', 'RevenueGrowth', 'EquityGrowth', 'EPSGrowth', 'BVPSGrowth', 'GrossProfitMargin', 'NetProfitMargin']
        st.bar_chart({key : temp_fund_avg[key]  for key in temp_fund_avg_key_order }, sort = False)
    else:
        st.html('Average of Fundamental data is not available')
    #! raw data
    # st.html(list(st.session_state.df_raw_fund.index))
    if stock_nav_selection[0] in list(st.session_state.df_raw_fund.index):    
        my_sector = list(st.session_state.df[ st.session_state.df['Code'] == stock_nav_selection[0] ]['GICs_industry_group'])[0]
        my_sector_companies = list(st.session_state.df[ st.session_state.df['GICs_industry_group'] == my_sector ]['Code'])
        my_sector_companies = list(set(my_sector_companies).intersection(set(st.session_state.df_raw_fund.index))) # remove missing companies
        my_sector_companies = list(set(my_sector_companies).difference(stock_nav_selection[0]))
        # st.html(my_sector_companies)
        temp_fund_raw = st.session_state.df_raw_fund.loc[stock_nav_selection[0] ]
        temp_raw_fund_melted = pd.melt(temp_fund_raw,
                               id_vars = 'Matric',
                               value_vars = sorted(list(temp_fund_raw.columns)[1:]),
                               var_name = 'year',
                               value_name = 'value')
        temp_raw_fund_melted['highlight'] = stock_nav_selection[0]
        # st.dataframe(temp_raw_fund_melted)
        #! repeat for all sector companies
        temp_fund_raw_sectors = st.session_state.df_raw_fund.loc[my_sector_companies]
        temp_raw_fund_sectors_melted = pd.melt(temp_fund_raw_sectors,
                               id_vars = 'Matric',
                               value_vars = sorted(list(temp_fund_raw_sectors.columns)[1:]),
                               var_name = 'year',
                               value_name = 'value')
        temp_raw_fund_sectors_melted['highlight'] = 'other'
        final_melted = pd.concat([temp_raw_fund_melted, temp_raw_fund_sectors_melted])
        final_melted = final_melted[ final_melted['value'] < 100 ]
        final_melted = final_melted[ final_melted['value'] > -100 ]

        # st.dataframe(final_melted)


        import plotly.express as px
        # fig = px.strip(
        #     df, 
        #     x="Matric", 
        #     y="value", 
        #     color="Matric",
        #     hover_data=["year"], 
        #     title="Metric Values by Year",
        #     labels={"value": "Percentage / Value", "Matric": "Financial Metric"}
        # )
        st.subheader('{} vs Sector performance (2020-2025)'.format(stock_nav_selection[0]))
        fig = px.strip(
            final_melted, 
            x="Matric", 
            y="value", 
            category_orders={"Matric": ['ROIC', 'RevenueGrowth', 'EquityGrowth', 'EPSGrowth', 'BVPSGrowth', 'FCFGrowth','GrossProfitMargin', 'NetProfitMargin', 'PercentRD_GrossProfit']},
            # title="Financial Metrics Distribution (2020-2025)",
            # points="all",       # Optional: displays all individual data points next to the box
            color="highlight",     # Optional: gives each box a different color
            labels={"value": "Percentage / Value", "Matric": "Financial Metric"}
        )

        # Improve layout for better readability of metric names
        fig.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.html('Raw Fundamental data is not available')

