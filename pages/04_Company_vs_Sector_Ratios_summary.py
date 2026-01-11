# ---- File: pages/record_view.py ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import re
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 6,          # General font size
    'axes.titlesize': 8,    # Subplot title size
    'axes.labelsize': 6,     # X and Y label size
    'xtick.labelsize': 5,    # X-axis tick size
    'ytick.labelsize': 5,    # Y-axis tick size
    'legend.fontsize': 5     # Legend size
})

dir_ticker_price = '/home/jay/Documents/python_stock_market/2024_July/yahooquery_more_data/data/prices/'
# ticker_price_avail = sorted([ c.replace('.AX_weekly.csv','')  for c in os.listdir(dir_ticker_price)])
## ---------------------------------------------------------------------------------
##! -- functions 
## ---------------------------------------------------------------------------------

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


# record = df.iloc[idx]
ticker_price_avail = set(df_cagr['Code'].to_list()).intersection( set(st.session_state.df_avg_fund.index) ).intersection( set(st.session_state.df_raw_fund.index ) )
ticker_price_avail = sorted(ticker_price_avail)

# with st.sidebar:
#     st.html('Data available on stocks: '+ str(len(ticker_price_avail)))
#     stock_nav_selection = [st.selectbox('Jump to ASX stock: ', ticker_price_avail)]
#     if st.button("Go"):
#         st.session_state.stocks = stock_nav_selection
#         st.rerun()
    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------
stock_nav_selection = st.session_state.stocks
if stock_nav_selection[0] in list(st.session_state.df_raw_fund.index):    
    my_sector = list(st.session_state.df[ st.session_state.df['Code'] == stock_nav_selection[0] ]['GICs_industry_group'])[0]
    my_sector_companies = list(st.session_state.df[ st.session_state.df['GICs_industry_group'] == my_sector ]['Code'])
    my_sector_companies = list(set(my_sector_companies).intersection(set(st.session_state.df_raw_fund.index))) # remove missing companies
    other_companies = list( set(my_sector_companies).difference(set([stock_nav_selection[0]])) )      
    # st.html(my_sector_companies)
    st.subheader('Yearly Fundamental Ratios: {} vs other companies in the "{}" sector'.format(stock_nav_selection[0], my_sector))
    st.html('<b>Other companies: </b>' + ', '.join(other_companies))
    temp_fund_raw = st.session_state.df_raw_fund.loc[my_sector_companies]
    temp_fund_raw['Type'] =[ stock_nav_selection[0] if c == stock_nav_selection[0] else 'other' for c in list(temp_fund_raw.index)]
    temp_fund_avg_key_order = ['ROIC', 'RevenueGrowth', 'GrossProfitMargin','EquityGrowth', 'EPSGrowth', 'BVPSGrowth']

    # st.dataframe(temp_fund_raw)
    # works for one matrix

    temp_raw_fund_melted = pd.melt(temp_fund_raw,
                        id_vars = ['Matric', 'Type'],
                        value_vars = set(range(2010,2100)).intersection(set(temp_fund_raw.columns)),
                        var_name = 'year',
                        value_name = 'value')
    # temp_raw_fund_melted = temp_raw_fund_melted[temp_raw_fund_melted['Matric'].isin(temp_fund_avg_key_order)]
    with st.container(width = 1600):
        g = sns.catplot(data = temp_raw_fund_melted,
                        x = 'year',
                        y = 'value',
                        col = 'Matric',
                        hue ='Type',
                        palette = {stock_nav_selection[0]: '#0041C2', 'other': '#9E9E9E'},
                        kind = 'bar',
                        col_wrap = 4,
                        col_order = temp_fund_avg_key_order,
                        height = 3, 
                        aspect= 0.8,
                        errorbar=None,
                        sharey=False, sharex = False)
        g.tick_params(axis='x', rotation=45)
        sns.move_legend(g, "lower left", bbox_to_anchor=(.5, .4), title = '' )
        sns.set_context("talk", font_scale=1.2)
        plt.setp(g._legend.get_texts(), fontsize='16') 
        plt.setp(g._legend.get_title(), fontsize='16')
        plt.tight_layout(pad=1.0)
        st.pyplot(g.fig, width='stretch')
else:
    st.html('Raw Fundamental data is not available')

