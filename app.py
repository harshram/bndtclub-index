import streamlit as st
import pandas as pd

st.write("Hello World!")

data = 'Index.xlsx'

Employment_ICT = pd.read_excel(data, sheet_name='Employment_ICT', skiprows=11, usecols="B:N")

#print(Employment_ICT)
st.dataframe(Employment_ICT)