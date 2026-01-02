# ---- File: Home.py ----
import streamlit as st
import pandas as pd
import os


@st.cache_data
def load_data(uploaded_file, sheet):
    df = pd.read_excel(uploaded_file,sheet_name = sheet)
    return df


st.set_page_config(page_title="Stock Fundamental Data Viewer")
st.session_state.fetchLiveData = st.checkbox('Fetch live data?', value = True)

os.listdir(os.getcwd())
uploaded_file = 'data/input.xlsx'
st.session_state.df = load_data(uploaded_file, "asx_index_filtered")
st.session_state.df_cagr = load_data(uploaded_file, "CAGR")
temp_avg_fund = load_data(uploaded_file, 'avg_fundamentals')
temp_avg_fund = temp_avg_fund.set_index('Code')
temp_avg_fund.index.name = None 
st.session_state.df_avg_fund = temp_avg_fund
#-- 
temp_raw_fund = load_data(uploaded_file, 'raw_fundamentals')
temp_raw_fund['Code'] = temp_raw_fund['Code'].apply(lambda x: x.split('.')[0]) 
temp_raw_fund = temp_raw_fund.set_index('Code')
temp_raw_fund.index.name = None 
temp_raw_fund = temp_raw_fund.rename( columns = {'Unnamed: 0': 'Matric'})
st.session_state.df_raw_fund = temp_raw_fund
##--
st.success('Data uploaded successfully!')
if st.button("Let's start"):
    st.session_state.stocks = ['CBA']
    st.switch_page("pages/Stocks_Dashboard.py")

