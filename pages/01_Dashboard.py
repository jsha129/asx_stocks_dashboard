# ---- File: pages/record_view.py ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import re
import matplotlib.pyplot as plt
import os
import seaborn as sns

## ---------------------------------------------------------------------------------
##! -- St page
## ---------------------------------------------------------------------------------
st.set_page_config(page_title="Record View", layout='wide')

if "df" not in st.session_state:
    st.error("Please go back and upload a file.")
    st.stop()



df = st.session_state.df
df_cagr = st.session_state.df_cagr
default_stock_indices = ['VTS', 'QUAL', 'VGS'] # NDQ MOAT has data from May 2015 onwards => affects charts

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
    # ##! Fundamental dats
    #! avg fundamental ratio
    if stock_nav_selection[0] in list(st.session_state.df_avg_fund.index):    
        temp_fund_avg = st.session_state.df_avg_fund.loc[stock_nav_selection[0] ]
        temp_fund_avg = temp_fund_avg.to_dict()
        # st.subheader('{}: {} year average of key ratios'.format(stock_nav_selection[0], str(int(temp_fund_avg['n']))))
        temp_fund_avg_key_order = ['ROIC', 'RevenueGrowth', 'EquityGrowth', 'EPSGrowth', 'BVPSGrowth', 'GrossProfitMargin', 'NetProfitMargin']
        with st.container(width=400): 
            fig, ax = plt.subplots()
            # plt.grid(True, alpha=0.3)
            # st.bar_chart({key : temp_fund_avg[key]  for key in temp_fund_avg_key_order }, sort = False, use_container_width=False)
            sns.barplot({key : temp_fund_avg[key]  for key in temp_fund_avg_key_order })
            ax.set_title('{}: {} year average of key ratios'.format(stock_nav_selection[0], str(int(temp_fund_avg['n']))))
            # ax.set_xlabel("Date")
            ax.set_ylabel("% values")
            plt.xticks(rotation=90)
            st.pyplot(fig)
    else:
        st.html('Average of Fundamental data is not available')    


with col2:
    # st.html('<b>Stock Performance</b>')
    if stock_nav_selection[0] in list(df_cagr['Code']):
        temp = df_cagr[ df_cagr['Code'] == stock_nav_selection[0] ][ ['Code', 'Sector','annual_growth_percent','r_squared', 'n', 'freq'] ]
        # st.html('<b>Code: </b>' + str(temp.iloc[0,0]))
        st.subheader(str(temp.iloc[0,0]))
        st.html('<b>Sector: </b>' + str(temp.iloc[0,1]))
        st.html('<b>Annual growth rate, CAGR: </b>' + str(temp.iloc[0,2]) + '%')
        st.html('<b>R-sqaured of the fit: </b>' + str(temp.iloc[0,3]))
        st.html('<b>Number of Weeks data: </b>' + str(temp.iloc[0,4]))
    else:
        st.html('Data not available')

    
   