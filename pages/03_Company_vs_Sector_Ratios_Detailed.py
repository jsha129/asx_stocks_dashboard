# ---- File: pages/record_view.py ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import re
import matplotlib.pyplot as plt
import os



## ---------------------------------------------------------------------------------
##! -- St page
## ---------------------------------------------------------------------------------
st.set_page_config(page_title="Record View", layout='wide')

if "df" not in st.session_state:
    st.error("Please go back and upload a file.")
    st.stop()

df = st.session_state.df
df_cagr = st.session_state.df_cagr
    
## ---------------------------------------------------------------------------------
##! Main page
## ---------------------------------------------------------------------------------


stock_nav_selection = st.session_state.stocks
if stock_nav_selection[0] in list(st.session_state.df_raw_fund.index):    
    my_sector = list(st.session_state.df[ st.session_state.df['Code'] == stock_nav_selection[0] ]['GICs_industry_group'])[0]
    my_sector_companies = list(st.session_state.df[ st.session_state.df['GICs_industry_group'] == my_sector ]['Code'])
    my_sector_companies = list(set(my_sector_companies).intersection(set(st.session_state.df_raw_fund.index))) # remove missing companies
    my_sector_companies = list( set(my_sector_companies).difference(set([stock_nav_selection[0]])) )
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
    st.html('Other Companies in the sector: ' + ', '.join(my_sector_companies))
    with st.container(width = 1000):
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
        st.plotly_chart(fig, width = 'content')

else:
    st.html('Raw Fundamental data is not available')

