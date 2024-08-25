import streamlit as st
import eurostat
import pandas as pd

st.write("Hello World!")

data = 'Index.xlsx'


'''
# hold approach by getting data from excel. Now data direclty from eurostat API
Employment_ICT = pd.read_excel(data, sheet_name='Employment_ICT', skiprows=11, usecols="B:N")
ICT_labour_demand = pd.read_excel(data, sheet_name='ICT_labor_demand', skiprows=8, usecols="B:L")
GVA_ICT_perc_of_total = pd.read_excel(data, sheet_name='ICT_GVA_perc_of_total', skiprows=11, usecols="B:M")
'''

# Load the dataset
GVA_data_import = eurostat.get_data_df('namq_10_a10_e')

# Rename the column since it only contains geographic information
if 'geo\\TIME_PERIOD' in GVA_data_import.columns:
    GVA_data_import.rename(columns={'geo\\TIME_PERIOD': 'geo'}, inplace=True)

# Melt the DataFrame to convert time columns into rows
GVA_data_melted = pd.melt(GVA_data_import, id_vars=['freq', 'unit','nace_r2','s_adj','na_item','geo'], var_name='time', value_name='value')
GVA_data_melted['quarter'] = pd.PeriodIndex(GVA_data_melted['time'], freq='Q')
GVA_data = GVA_data_melted[(GVA_data_melted['quarter'] >= '2010Q1')]
GVA_data = GVA_data.drop(columns=['time','freq'])

# Display the melted DataFrame to verify the structure
st.write("Melted DataFrame:")
#st.dataframe(GVA_data_import)
#st.dataframe(GVA_data_melted.sample(1000))
st.dataframe(GVA_data.sample(1000))
