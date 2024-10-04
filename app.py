import ternary
import mpltern
import eurostat
import json

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.cm as cm 
import plotly.express as px

from text_to_print import description_text, description_text_by_quarter
from sklearn.preprocessing import MinMaxScaler  # Or use StandardScaler for Z-score normalization
from data_processing import process_import_data, process_ICT_labour_import_data

# Set the page configuration at the top of the script
st.set_page_config(
    page_title="B&DT Club Digital Transformation Index",  # Optional: Give your app a title
    layout="centered"  # Using the centered layout
)

# Sidebar for navigation
page1 = "DTPI vesion 0"
page2 = "DTPI version 0.1"
page3 = "DTPI deployment test"
page4 = "DTPI recurring tab"
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [page1, page2, page3,page4])


# Inject custom CSS to control the width of the centered layout
st.markdown(
    """
    <style>
    /* Adjust the width of the block-container class */
    .block-container {
        max-width: 1200px;  /* Adjust this value to control the width */
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Normalize the data using Min-Max scaling
scaler = MinMaxScaler()

# List of countries for which to process and plot data
# List of countries and titles
countries = ['IT', 'FR', 'DE', 'ES', 'NL']
country_titles = ['Italy (IT)', 'France (FR)', 'Germany (DE)', 'Spain (ES)', 'Netherlands (NL)']
#countries = ['IT', 'FR', 'DE']  # Italy, France, and Germany

# Caching data to save time in loading data from API call
@st.cache_data
def load_data():
    # Load the raw data from Eurostat API
    GVA_data_import = eurostat.get_data_df('namq_10_a10')
    print("Got GVA data")
    Employment_data_import = eurostat.get_data_df('namq_10_a10_e')
    print("Got Employment data")
    Labour_demand_ICT_data_import = eurostat.get_data_df('isoc_sk_oja1')
    print("Got Labour Demand data")

    # Define the starting quarter for filtering data
    date_start = '2019Q4'

    # Process the raw data
    GVA_data = process_import_data(GVA_data_import, date_start)
    Employment_data = process_import_data(Employment_data_import, date_start)
    Labour_demand_ICT_data = process_ICT_labour_import_data(Labour_demand_ICT_data_import, date_start)

    return GVA_data, Employment_data, Labour_demand_ICT_data

# Load the data from the cached function
GVA_data, Employment_data, Labour_demand_ICT_data = load_data()

print("All data has been loaded")

# Initialize dictionaries to hold country-specific filtered data
filtered_data = {'GVA': {}, 'Employment': {}, 'LabourDemand': {}}

# Filter data for each country and normalize
for country in countries:
    filtered_data['GVA'][country] = GVA_data[(GVA_data['nace_r2'] == 'J') & 
                                             (GVA_data['unit'] == 'PC_GDP') & 
                                             (GVA_data['geo'] == country) & 
                                             (GVA_data['na_item'] == 'B1G') & 
                                             (GVA_data['s_adj'] == 'NSA')].copy()

    filtered_data['Employment'][country] = Employment_data[(Employment_data['nace_r2'] == 'J') & 
                                                           (Employment_data['unit'] == 'PC_TOT_PER') & 
                                                           (Employment_data['geo'] == country) & 
                                                           (Employment_data['na_item'] == 'EMP_DC') & 
                                                           (Employment_data['s_adj'] == 'NSA')].copy()

    filtered_data['LabourDemand'][country] = Labour_demand_ICT_data[(Labour_demand_ICT_data['geo'] == country) &
                                                                    (Labour_demand_ICT_data['unit'] == 'PC')].copy()

    # Convert 'quarter' from Period to string format for proper labeling
    filtered_data['GVA'][country]['quarter'] = filtered_data['GVA'][country]['quarter'].dt.strftime('%Y-Q%q')
    filtered_data['Employment'][country]['quarter'] = filtered_data['Employment'][country]['quarter'].dt.strftime('%Y-Q%q')
    filtered_data['LabourDemand'][country]['quarter'] = filtered_data['LabourDemand'][country]['quarter'].dt.strftime('%Y-Q%q')

    # Normalize the data
    filtered_data['GVA'][country]['normalized_value'] = scaler.fit_transform(filtered_data['GVA'][country][['value']])
    filtered_data['Employment'][country]['normalized_value'] = scaler.fit_transform(filtered_data['Employment'][country][['value']])
    filtered_data['LabourDemand'][country]['normalized_value'] = scaler.fit_transform(filtered_data['LabourDemand'][country][['value']])

print("Filtered and normalised all values")

# Set global font size for plots
plt.rcParams.update({'font.size': 12})

# Parametrizable window for gradient calculation
window = st.sidebar.slider("Select Gradient Window", 1, 10, 2)  # Slider to select the window size
def custom_gradient(data, window):
    return (data - data.shift(window)) / window

# Initialize an empty DataFrame to hold raw and normalized custom gradients
custom_gradients_df = pd.DataFrame()

for country in countries:
    # Set 'quarter' as the index for each dataset
    employment_data = filtered_data['Employment'][country].set_index('quarter')
    GVA_data = filtered_data['GVA'][country].set_index('quarter')
    labour_data = filtered_data['LabourDemand'][country].set_index('quarter')  # Ensure correct LabourDemand key

    # Define a dictionary to store raw and normalized gradients for each dataset
    gradients = {}

    # List of datasets to loop over
    datasets = {
        'employment': employment_data,
        'GVA': GVA_data,
        'labour': labour_data
    }

    # Loop over each dataset and calculate the raw and normalized gradients
    for data_key, data in datasets.items():
        # Calculate the custom gradient for the current dataset
        custom_grad = custom_gradient(data['value'], window).dropna()
        # Normalize the custom gradient using MinMaxScaler
        normalized_grad = scaler.fit_transform(custom_grad.values.reshape(-1, 1)).flatten()

        # Store the raw and normalized gradients in the gradients dictionary
        gradients[f'{data_key}_grad_{country}'] = pd.Series(custom_grad, index=custom_grad.index)
        gradients[f'normalized_{data_key}_grad_{country}'] = pd.Series(normalized_grad, index=custom_grad.index)

    # Create a DataFrame for this country’s gradients
    country_gradients_df = pd.DataFrame(gradients)

    # Concatenate the current country's DataFrame with the main DataFrame
    # Align on the 'quarter' index using axis=1 to ensure each country gets its own columns
    custom_gradients_df = pd.concat([custom_gradients_df, country_gradients_df], axis=1)

# Initialize an empty DataFrame to hold the index values for all countries
index_data = pd.DataFrame()

plt.figure(figsize=(4, 3), dpi=150)

for country in countries:    
    index_data[country] = custom_gradients_df[f'normalized_employment_grad_{country}']*custom_gradients_df[f'normalized_GVA_grad_{country}']*custom_gradients_df[f'normalized_labour_grad_{country}']
    index_data.index = custom_gradients_df.index


# The final DataFrame will automatically handle different lengths because of concatenation
#st.write('Custom gradients (raw and normalized) for Employment, GVA, and Labour Demand across countries')
#st.dataframe(custom_gradients_df)

if page == page1:
    # Create two columns for the plots
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])


    # Plot overlapping Employment, GVA, and Labour demand data for all countries
    with col1:
        st.write('Ordinary values')
        # Plot Employment data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o', label=f'Employment - {country}')
        plt.title('Employment Data for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of Total Employees')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        # Plot GVA data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o', label=f'GVA - {country}')
        plt.title('GVA Data for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of GDP')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        # Plot Labour demand data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o', label=f'Labour Demand - {country}')
        plt.title('Labour Demand for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of total job advertisement online')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    with col2:
        st.write('Normalized values')
        # Plot Normalized Employment data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['normalized_value'], marker='o', label=f'Normalized Employment - {country}')
        plt.title('Normalized Employment Data for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Percentage of Total Employees')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        # Plot Normalized GVA data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['normalized_value'], marker='o', label=f'Normalized GVA - {country}')
        plt.title('Normalized GVA Data for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Percentage of GDP')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        # Plot Normalized Labour demand data for all countries
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['normalized_value'], marker='o', label=f'Normalized Labour Demand - {country}')
        plt.title('Normalized Labour Demand for IT, FR, DE (Industry J)')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Percentage of total job advertisement online')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot moving averages with window=2 in col3
    with col3:
        st.write('Moving averages (window = 2)')
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['Employment'][country]['normalized_value'].rolling(window=2).mean()
            plt.plot(filtered_data['Employment'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Employment (w=2) - {country}')
        plt.title('Moving Average of Employment for IT, FR, DE (window = 2)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['GVA'][country]['normalized_value'].rolling(window=2).mean()
            plt.plot(filtered_data['GVA'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg GVA (w=2) - {country}')
        plt.title('Moving Average of GVA for IT, FR, DE (window = 2)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['LabourDemand'][country]['normalized_value'].rolling(window=2).mean()
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Labour Demand (w=2) - {country}')
        plt.title('Moving Average of Labour Demand for IT, FR, DE (window = 2)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot moving averages with window=3 in col4
    with col4:
        st.write('Moving averages (window = 3)')
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['Employment'][country]['normalized_value'].rolling(window=3).mean()
            plt.plot(filtered_data['Employment'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Employment (w=3) - {country}')
        plt.title('Moving Average of Employment for IT, FR, DE (window = 3)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['GVA'][country]['normalized_value'].rolling(window=3).mean()
            plt.plot(filtered_data['GVA'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg GVA (w=3) - {country}')
        plt.title('Moving Average of GVA for IT, FR, DE (window = 3)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['LabourDemand'][country]['normalized_value'].rolling(window=3).mean()
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Labour Demand (w=3) - {country}')
        plt.title('Moving Average of Labour Demand for IT, FR, DE (window = 3)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot moving averages with window=4 in col5
    with col5:
        st.write('Moving averages (window = 4)')
        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['Employment'][country]['normalized_value'].rolling(window=4).mean()
            plt.plot(filtered_data['Employment'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Employment (w=4) - {country}')
        plt.title('Moving Average of Employment for IT, FR, DE (window = 4)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['GVA'][country]['normalized_value'].rolling(window=4).mean()
            plt.plot(filtered_data['GVA'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg GVA (w=4) - {country}')
        plt.title('Moving Average of GVA for IT, FR, DE (window = 4)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_avg = filtered_data['LabourDemand'][country]['normalized_value'].rolling(window=4).mean()
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], moving_avg, marker='o', label=f'Moving Avg Labour Demand (w=4) - {country}')
        plt.title('Moving Average of Labour Demand for IT, FR, DE (window = 4)')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Average')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    st.divider()
    st.latex(r'''
    \text{Derivative}(t) = \frac{x(t+1) - x(t)}{t_{i+1} - t_i}
    ''')

    st.latex(r'''
    \text{Moving Derivative (Window = 2)} = \frac{x(t+2) - x(t)}{t_{i+2} - t_i}
    ''')

    st.latex(r'''
    \text{Moving Derivative (Window = 3)} = \frac{x(t+3) - x(t)}{t_{i+3} - t_i}
    ''')

    # Create four columns for the plots
    col1, col2, col3, col4 = st.columns([4, 4, 4, 4])

    # Plot normalized values in col1
    with col1:
        st.write('Normalized values')

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['normalized_value'], marker='o', label=f'Normalized Employment - {country}')
        plt.title('Normalized Employment Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Value')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['normalized_value'], marker='o', label=f'Normalized GVA - {country}')
        plt.title('Normalized GVA Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Value')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['normalized_value'], marker='o', label=f'Normalized Labour Demand - {country}')
        plt.title('Normalized Labour Demand Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Value')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot derivatives in col2 (Derivative between consecutive points)
    with col2:
        st.write('Derivatives')

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            derivative = np.gradient(filtered_data['Employment'][country]['normalized_value'], edge_order=2)
            plt.plot(filtered_data['Employment'][country]['quarter'], derivative, marker='o', label=f'Derivative Employment - {country}')
        plt.title('Derivative of Employment for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            derivative = np.gradient(filtered_data['GVA'][country]['normalized_value'], edge_order=2)
            plt.plot(filtered_data['GVA'][country]['quarter'], derivative, marker='o', label=f'Derivative GVA - {country}')
        plt.title('Derivative of GVA for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            derivative = np.gradient(filtered_data['LabourDemand'][country]['normalized_value'], edge_order=2)
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], derivative, marker='o', label=f'Derivative Labour Demand - {country}')
        plt.title('Derivative of Labour Demand for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot moving derivative with window=2 in col3
    with col3:
        st.write('Moving Derivative (window = 2)')

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            # Moving Derivative with Window = 2
            moving_derivative_2 = (filtered_data['Employment'][country]['normalized_value'].shift(2) - filtered_data['Employment'][country]['normalized_value']) / 2
            moving_derivative_2 = moving_derivative_2.dropna()  # Drop NaN values
            quarters_2 = filtered_data['Employment'][country]['quarter'][moving_derivative_2.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_2, moving_derivative_2, marker='o', label=f'Moving Derivative Employment (w=2) - {country}')
        plt.title('Moving Derivative of Employment (window = 2) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_derivative_2 = (filtered_data['GVA'][country]['normalized_value'].shift(2) - filtered_data['GVA'][country]['normalized_value']) / 2
            moving_derivative_2 = moving_derivative_2.dropna()  # Drop NaN values
            quarters_2 = filtered_data['GVA'][country]['quarter'][moving_derivative_2.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_2, moving_derivative_2, marker='o', label=f'Moving Derivative GVA (w=2) - {country}')
        plt.title('Moving Derivative of GVA (window = 2) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_derivative_2 = (filtered_data['LabourDemand'][country]['normalized_value'].shift(2) - filtered_data['LabourDemand'][country]['normalized_value']) / 2
            moving_derivative_2 = moving_derivative_2.dropna()  # Drop NaN values
            quarters_2 = filtered_data['LabourDemand'][country]['quarter'][moving_derivative_2.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_2, moving_derivative_2, marker='o', label=f'Moving Derivative Labour Demand (w=2) - {country}')
        plt.title('Moving Derivative of Labour Demand (window = 2) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # Plot moving derivative with window=3 in col4
    with col4:
        st.write('Moving Derivative (window = 3)')

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            # Moving Derivative with Window = 3
            moving_derivative_3 = (filtered_data['Employment'][country]['normalized_value'].shift(3) - filtered_data['Employment'][country]['normalized_value']) / 3
            moving_derivative_3 = moving_derivative_3.dropna()  # Drop NaN values
            quarters_3 = filtered_data['Employment'][country]['quarter'][moving_derivative_3.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_3, moving_derivative_3, marker='o', label=f'Moving Derivative Employment (w=3) - {country}')
        plt.title('Moving Derivative of Employment (window = 3) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_derivative_3 = (filtered_data['GVA'][country]['normalized_value'].shift(3) - filtered_data['GVA'][country]['normalized_value']) / 3
            moving_derivative_3 = moving_derivative_3.dropna()  # Drop NaN values
            quarters_3 = filtered_data['GVA'][country]['quarter'][moving_derivative_3.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_3, moving_derivative_3, marker='o', label=f'Moving Derivative GVA (w=3) - {country}')
        plt.title('Moving Derivative of GVA (window = 3) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        plt.figure(figsize=(12, 8), dpi=100)
        for country in countries:
            moving_derivative_3 = (filtered_data['LabourDemand'][country]['normalized_value'].shift(3) - filtered_data['LabourDemand'][country]['normalized_value']) / 3
            moving_derivative_3 = moving_derivative_3.dropna()  # Drop NaN values
            quarters_3 = filtered_data['LabourDemand'][country]['quarter'][moving_derivative_3.index]  # Align quarters with non-NaN derivatives
            plt.plot(quarters_3, moving_derivative_3, marker='o', label=f'Moving Derivative Labour Demand (w=3) - {country}')
        plt.title('Moving Derivative of Labour Demand (window = 3) for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Moving Derivative')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)




    # Merging the datasets for IT, FR, and DE
    merged_data = pd.DataFrame()
    for country in countries:
        temp = pd.merge(filtered_data['Employment'][country][['quarter', 'normalized_value']], 
                        filtered_data['GVA'][country][['quarter', 'normalized_value']], 
                        on='quarter', suffixes=('_employment', '_gva'))

        # Rename the normalized_value column before merging
        filtered_data['LabourDemand'][country] = filtered_data['LabourDemand'][country].rename(columns={'normalized_value': 'normalized_value_labour_demand'})

        # Merge the DataFrames
        temp = pd.merge(temp, 
                    filtered_data['LabourDemand'][country][['quarter', 'normalized_value_labour_demand']], 
                    on='quarter')

        
        temp['delta_normalized_labour_demand'] = temp['normalized_value_labour_demand'].shift(1) - temp['normalized_value_labour_demand']

        temp['Index1'] = 0.333*temp['normalized_value_employment'] + 0.333*temp['normalized_value_gva'] + 0.333*temp['normalized_value_labour_demand']
        temp['Index2'] = temp['normalized_value_gva'] * (temp['normalized_value_employment'] + temp['normalized_value_labour_demand'])
        temp['Index3'] = temp['normalized_value_gva'] * (1 + temp['normalized_value_employment'] + temp['normalized_value_labour_demand'])
        temp['Index4'] = (temp['normalized_value_gva']/(temp['normalized_value_employment']+0.001))*(1+temp['delta_normalized_labour_demand'])
        temp['Index5'] = np.log((temp['normalized_value_gva'] + 1)/(temp['normalized_value_employment']+0.001))*(1+temp['delta_normalized_labour_demand'])

        temp['country'] = country
        merged_data = pd.concat([merged_data, temp])

    # Divider before the "Index Tests" section
    st.divider()

    # Display the index 1 formula before plotting
    st.write('Index tests')
    #st.write("## Index Formula:")
    st.write('###Digital Transformation Potential Index (DTPI)')

    st.write('DTPI1: Simple, assumes equal contribution of all factors. Easy to understand but treats components as fully substitutable.')
    st.latex(r'''
                DTPI_1 =  \frac{1}{3} \times GVA_{\text{norm}} \times \frac{1}{3} \text{Emp}_{\text{norm}} + \frac{1}{3} \text{Demand}_{\text{norm}}
                ''')

    # Plot Index for all countries
    plt.figure(figsize=(12, 8), dpi=100)
    for country in countries:
        country_data = merged_data[merged_data['country'] == country]
        plt.plot(country_data['quarter'], country_data['Index1'], marker='o', label=f'Index - {country}')
    plt.title('DTPI1 for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('[-]')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)


    st.write('DTPI2: Highlights GVA’s impact with employment/demand trends. More sensitive to extreme values, emphasizing magnitude and trends.')
    st.latex(r'''
        DTPI_2 = GVA_{\text{norm}} \times \left( \text{Emp}_{\text{norm}} + \text{Demand}_{\text{norm}} \right)
        ''')
    # Plot Index for all countries
    plt.figure(figsize=(12, 8), dpi=100)
    for country in countries:
        country_data = merged_data[merged_data['country'] == country]
        plt.plot(country_data['quarter'], country_data['Index2'], marker='o', label=f'Index - {country}')
    plt.title('DTPI2 for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('[-]')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write('DTPI3: Balances components multiplicatively, reducing extreme impacts. Reflects that all areas must perform well for higher scores.')
    st.latex(r'''
        DTPI_3 = GVA_{\text{norm}} \times \left( 1 + \text{Emp}_{\text{norm}} + \text{Demand}_{\text{norm}} \right)
        ''')
    # Plot Index for all countries
    plt.figure(figsize=(12, 8), dpi=100)
    for country in countries:
        country_data = merged_data[merged_data['country'] == country]
        plt.plot(country_data['quarter'], country_data['Index3'], marker='o', label=f'Index - {country}')
    plt.title('DTPI3 for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('[-]')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write('DTPI4: Uses variation of labour demand and divides GVA by employment to scale effect of GVA over number people in the workforce')
    st.latex(r'''
        \text{DTPI}_4 = \frac{\text{GVA}_{\text{norm}}}{\text{Emp}_{\text{norm}} + \epsilon} \times (1 + \Delta \text{Demand}_{\text{norm}})
    ''')
    st.write('epsilo = 0.001')


    # Plot Index for all countries
    plt.figure(figsize=(12, 8), dpi=100)
    for country in countries:
        country_data = merged_data[merged_data['country'] == country]
        plt.plot(country_data['quarter'], country_data['Index4'], marker='o', label=f'Index - {country}')
    plt.title('DTPI4 for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('[-]')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)


    st.write('DTPI5: Uses variation of labour demand and divides GVA by employment to scale effect of GVA over number people in the workforce')
    st.latex(r'''
        \text{DTPI}_5 = \log\left( \frac{\text{GVA}_{\text{norm}} + 1}{\text{Emp}_{\text{norm}} + \epsilon} \right) \times (1 + \Delta \text{Demand}_{\text{norm}})
    ''')
    st.write('epsilo = 0.001')
    st.write("""
    ### Index Explanation:

    - **Efficiency:** The term \\(\\frac{\\text{GVA}_{\\text{norm}} + 1}{\\text{Emp}_{\\text{norm}} + \\epsilon}\\) measures how efficiently value is created with the available workforce. A higher result means better efficiency, indicating more value is created with fewer workers.
    
    - **Logarithmic Transformation:** The efficiency term is inside a log to prevent extreme values, especially when employment is low. The log compresses large values, ensuring smoother, more stable results and focusing on proportional differences rather than absolute ones. This prevents the index from being skewed by outliers.

    - **+1 in GVA:** Adding +1 ensures the log function works even when GVA is small or zero, avoiding calculation errors and keeping the index meaningful.

    - **Future Potential:** The term \\(1 + \\Delta \\text{Demand}_{\\text{norm}}\\) reflects labor demand trends, indicating the sector's future growth potential based on increasing or decreasing demand.

    - **Numerical Stability:** The small constant \\(\\epsilon\\) in the denominator prevents division by zero, ensuring stable and robust calculations.
    """)


    # Plot Index for all countries
    plt.figure(figsize=(12, 8), dpi=100)
    for country in countries:
        country_data = merged_data[merged_data['country'] == country]
        plt.plot(country_data['quarter'], country_data['Index5'], marker='o', label=f'Index - {country}')
    plt.title('DTPI5 for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('[-]')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write("""
    ### Italy (Index - IT):
    Italy starts with moderate values early in 2020 but shows significant fluctuations through the later periods.  
    Peaks in Q4 2020 and Q4 2021 suggest that in these periods, Italy had high relative GVA efficiency (likely higher GVA with moderate or lower workforce size) combined with rising labor demand, leading to a positive outlook.  
    However, after these spikes, the index values drop dramatically, suggesting labor demand stagnated or decreased, impacting future prospects despite stable or improved efficiency.

    ### France (Index - FR):
    France shows a steep decline early in 2020, starting at a high point and dropping sharply by Q2 2020.  
    This could indicate an initial period of higher GVA with lower workforce followed by a rapid drop in labor demand or worsening efficiency.  
    The trend stabilizes in 2021 and 2022, with lower but consistent values. This suggests that France had relatively stable, albeit lower, efficiency and labor demand after the initial decline, with no major growth prospects in the near future.

    ### Germany (Index - DE):
    Germany’s index starts high in Q1 2020, similar to Italy and France, but maintains a more consistent performance compared to the others.  
    While Germany does have a notable drop after Q1 2020, it doesn't experience the dramatic fluctuations seen in Italy. Instead, the index remains fairly steady, hovering around moderate values.  
    This suggests that Germany maintained stable efficiency (GVA-to-workforce ratio) with relatively consistent labor demand trends. The lack of major peaks or valleys implies neither a significant boom nor bust in its digital transformation potential over time.

    ### Overall Trend:
    Italy and France show more volatile trends, indicating fluctuating GVA efficiency and labor demand. Italy has strong spikes but also rapid drops, suggesting inconsistent future prospects.  
    Germany shows more stability in its digital transformation potential, implying a more gradual, consistent development without major volatility in efficiency or demand trends.
    """)

elif page == page2:

    st.title("Version 0.1: multipliers-based")
    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Column 1: ICT Employment Data
    with col1:
        st.write("**ICT Employment Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o', label=f'{country}')
        plt.title('ICT Employment Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of Total Employees')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write("**GVA Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o', label=f'{country}')
        plt.title('GVA Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of GDP')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write("**Labour Demand Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o', label=f'{country}')
        plt.title('Labour Demand Data for IT, FR, DE')
        plt.xlabel('Quarter')
        plt.ylabel('Percentage of Total Job Advertisements Online')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)


    with col2:
        st.write(f"**Gradient with Window = {window} for ICT Employment Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'employment_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'ICT Employment Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel(' Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write(f"**Gradient with Window = {window} for GVA Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'GVA_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'GVA Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel('Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write(f"**Gradient with Window = {window} for Labour Demand Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'labour_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'Labour Demand Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel('Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)


        # Column 3: Normalized custom gradient values using MinMaxScaler
    with col3:
        st.write(f"**Normalized Gradient with Window = {window} for ICT Employment Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'normalized_employment_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'Normalized ICT Employment Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write(f"**Normalized Gradient with Window = {window} for GVA Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'normalized_GVA_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'Normalized GVA Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

        st.write(f"**Normalized Gradient with Window = {window} for Labour Demand Data**")
        plt.figure(figsize=(8, 6))
        for country in countries:
            plt.plot(custom_gradients_df.index, custom_gradients_df[f'normalized_labour_grad_{country}'], marker='o', label=f'{country}')
        plt.title(f'Normalized Labour Demand Gradient for IT, FR, DE (Window = {window})')
        plt.xlabel('Quarter')
        plt.ylabel('Normalized Gradient')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    st.write(f"**Index Calculation (Normalized ICT Employment × Normalized GVA × Normalized Labour Demand)**")
    # Initialize an empty DataFrame to hold the index values for all countries

    plt.figure(figsize=(4, 3), dpi=150)

    for country in countries:
      # Plot the index values for this country
        plt.plot(index_data.index, index_data[f'{country}'], marker='o', label=f'{country}')


    # Set the plot title and labels outside the loop
    plt.title('Index for IT, FR, DE')
    plt.xlabel('Quarter')
    plt.ylabel('Index Value')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    # Display the plot in Streamlit
    st.pyplot(plt)

    col_GVA, col_indx = st.columns(2)

    country_titles = ['Italy (IT)', 'France (FR)', 'Germany (DE)']

    # In the left column, plot GVA data
    with col_GVA:
        st.write("**GVA Data for IT, FR, DE**")
        for i, country in enumerate(countries):
            gva_data = filtered_data['GVA'][country]['value']
            quarter = filtered_data['GVA'][country]['quarter']

            plt.figure(figsize=(8, 6))
            plt.plot(quarter, gva_data, marker='o', label=f'{country} GVA', color='blue')
            plt.title(f'GVA for {country_titles[i]}')
            plt.xlabel('Quarter')
            plt.ylabel('GVA (% of GDP)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            st.pyplot(plt)

    # In the right column, plot the precomputed custom index
    with col_indx:
        st.write("**Custom Index for IT, FR, DE**")
        for i, country in enumerate(countries):
            # Use the precomputed custom index from the previous code
            #index = index_data[country]  # Assuming you have stored the precomputed index in a dictionary or similar structure
            

            # Plot the custom index
            plt.figure(figsize=(8, 6))
            plt.plot(index_data.index, index_data[f'{country}'], marker='o', label=f'{country} Index', color='green')
            plt.title(f'Custom Index for {country_titles[i]}')
            plt.xlabel('Quarter')
            plt.ylabel('Custom Index')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            st.pyplot(plt)

elif page==page3:

    st.title("DTPI - Selected countries")

    # Create three tabs, one for each country
    tab1, tab2, tab3, tab4 = st.tabs(["DTPI - what is it", "Italy (IT)", "France (FR)", "Germany (DE)"])

    with tab1:
        st.title("Digital Transformation Potential Index (DTPI)")

        st.write("""
        The **Digital Transformation Potential Index (DTPI)** is a composite measure designed to assess a country’s capability to drive economic and social development through digital innovation. The index leverages three key indicators from the ICT sector:
        
        1. **Gross Value Added (GVA)** – This measures the economic value generated by the ICT sector. High GVA suggests a country is deriving significant value from its digital industries.
    
        2. **ICT Employment** – This captures the proportion of the workforce employed in ICT-related sectors. A larger ICT workforce indicates a higher engagement with digital technologies and services, though this must be balanced with the efficiency seen in GVA.

        3. **Labor Demand Trends** – This tracks shifts in the demand for ICT-related skills, providing insights into how future-ready a country’s workforce is for digital transformation.
        
        ### Key Features of the Index:
        - **GVA Efficiency**: The index favors countries with high GVA but relatively low ICT workforce, highlighting those that achieve more with fewer resources. Conversely, a large ICT workforce paired with low GVA indicates inefficiencies.
    
        - **Labor Demand as a Future Indicator**: Countries with rising demand for ICT skills are seen as having greater potential for future digital transformation. This measure accounts for the evolving needs of the digital economy, reflecting how well-positioned a country’s workforce is to meet these demands.

        ### What the DTPI Delivers:
        By combining these indicators, the DTPI provides a holistic view of a country’s digital transformation readiness, helping stakeholders understand where to invest, which countries are leading the digital revolution, and where challenges might lie. This index can serve policymakers, businesses, and researchers looking to understand the economic impacts of ICT development on a macro level.
        """)

        st.write("""
        This application visualizes these indicators for selected countries and offers different index calculations to provide insights into how GVA, ICT Employment, and Labor Demand Trends impact digital transformation readiness.
        """)

    # Tab 1: Italy (IT)
    with tab2:
        st.write("### Italy (IT)")
        
        col1, col2 = st.columns([1, 2])
            
        # Column 1 content: ICT Employment, GVA, and Labour Demand Data
        with col1:
            st.write("**ICT Employment Data**")
            fig1, ax1 = plt.subplots(figsize=(4, 3))  # Adjust figure size
            ax1.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o')
            ax1.set_title(f'ICT Employment Data for {country}', fontsize=12)
            ax1.set_xlabel('Quarter', fontsize=10)
            ax1.set_ylabel('Percentage of Total Employees', fontsize=10)
            ax1.grid(True)  # Add grid to the plot
            ax1.tick_params(axis='x', rotation=45, labelsize=9)
            ax1.tick_params(axis='y', labelsize=9)
            st.pyplot(fig1)

            st.write("**GVA Data**")
            fig2, ax2 = plt.subplots(figsize=(4, 3))  # Adjust figure size
            ax2.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o')
            ax2.set_title(f'GVA Data for {country}', fontsize=12)
            ax2.set_xlabel('Quarter', fontsize=10)
            ax2.set_ylabel('Percentage of GDP', fontsize=10)
            ax2.grid(True)  # Add grid to the plot
            ax2.tick_params(axis='x', rotation=45, labelsize=9)
            ax2.tick_params(axis='y', labelsize=9)
            st.pyplot(fig2)

            st.write("**Labour Demand Data**")
            fig3, ax3 = plt.subplots(figsize=(4, 3))  # Adjust figure size
            ax3.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o')
            ax3.set_title(f'Labour Demand Data for {country}', fontsize=12)
            ax3.set_xlabel('Quarter', fontsize=10)
            ax3.set_ylabel('Percentage of Total Job Advertisements Online', fontsize=10)
            ax3.grid(True)  # Add grid to the plot
            ax3.tick_params(axis='x', rotation=45, labelsize=9)
            ax3.tick_params(axis='y', labelsize=9)
            st.pyplot(fig3)

        # Column 2 content: Index plot and bubble chart
        with col2:
            st.write("**Index for Italy (IT)**")
            fig_index, ax_index = plt.subplots(figsize=(5, 4))  # Adjust figure size
            ax_index.plot(index_data.index, index_data['IT'], marker='o', label='Italy (IT)')
            ax_index.set_title('Index for Italy (IT)', fontsize=12)
            ax_index.set_xlabel('Quarter', fontsize=10)
            ax_index.set_ylabel('Index Value', fontsize=10)
            ax_index.grid(True)  # Add grid to the plot
            ax_index.tick_params(axis='x', rotation=45, labelsize=9)
            ax_index.tick_params(axis='y', labelsize=9)
            st.pyplot(fig_index)

            # Set bubble plot dimensions to align properly
            custom_gradients_df_with_index = custom_gradients_df.reset_index().rename(columns={'index': 'quarter'})
            
            # Adjust Plotly figure size using layout controls
            fig_bubble = px.scatter(
                custom_gradients_df_with_index,
                x='normalized_employment_grad_IT',
                y='normalized_labour_grad_IT',
                size='normalized_GVA_grad_IT',
                hover_name='quarter',
                animation_frame='quarter',
            )

            fig_bubble.update_layout(
                width=600,  # Adjust width to match layout
                height=400,  # Adjust height to align with left column
                margin=dict(l=20, r=20, t=30, b=20),  # Adjust margins for better alignment
                xaxis_title="Normalized Employment Growth",  # Add x-axis label
                yaxis_title="Normalized Labour Growth",  # Add y-axis label
                font=dict(size=10),  # Set overall font size for the plot
                title_font=dict(size=12),  # Set title font size
                hoverlabel=dict(font_size=9),  # Adjust hover text font size
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),  # Add grid to x-axis
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),  # Add grid to y-axis
            )

            st.plotly_chart(fig_bubble)

        st.write("""
            ### **How the DTPI Reflects the Evolution of Inputs**

            - **Early Period (2020-Q4 to 2021-Q2)**:  
            The sharp drop in the index mirrors the significant decline in **GVA**, despite relatively stable **ICT Employment** and moderate **Labour Demand**. The index reflects inefficiency in the ICT sector during this time, where economic output declines faster than employment growth, signaling underperformance.

            - **Stagnation Phase (2021-Q2 to 2022-Q1)**:  
            During this period, the index remains low as **GVA** stays depressed, **Labour Demand** decreases, and **ICT Employment** grows only slightly. The index captures this stagnation by reflecting a lack of significant improvements in economic output or future job creation, showing minimal potential for growth.

            - **Recovery and Growth (2022-Q2 to 2023-Q1)**:  
            As **GVA** increases and **ICT Employment** expands, the index rises sharply. This indicates improved efficiency in the ICT sector. The stabilization and rise in **Labour Demand** further boosts the index, signaling positive future expectations.

            - **Recent Volatility (2023-Q2 to 2024-Q1)**:  
            The index becomes more volatile, reflecting fluctuations in **GVA** and **Labour Demand**, while **ICT Employment** remains relatively stable. The instability in the index mirrors the uncertain future prospects for the ICT sector, with both potential growth and risks present.
            """)


            
            

    # Tab 2: France (FR)
    with tab3:
        st.write("### France (FR)")
        
        col1, col2= st.columns([1,2])
        
        # Column 1: 
        with col1:
            st.write("**ICT Employment Data**")
            plt.figure(figsize=(8, 6))
            country = 'FR'
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'ICT Employment Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of Total Employees')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)
        
            st.write("**GVA Data**")
            plt.figure(figsize=(8, 6))
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'GVA Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of GDP')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)

            st.write("**Labour Demand Data**")
            plt.figure(figsize=(8, 6))
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'Labour Demand Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of Total Job Advertisements Online')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)
        
        with col2:
            st.write("**Index**")
            # Plot the index for France (FR)
            plt.figure(figsize=(6, 10), dpi=150)
            plt.plot(index_data.index, index_data['FR'], marker='o', label='France (FR)')
            plt.title('Index for France (FR)')
            plt.xlabel('Quarter')
            plt.ylabel('Index Value')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)

         # Temporarily add the index (quarters) as a column for hover_name
        custom_gradients_df_with_index = custom_gradients_df.reset_index().rename(columns={'index': 'quarter'})

        fig = px.scatter(
            custom_gradients_df_with_index,  # Reset index temporarily for the plot
            x='normalized_employment_grad_FR',
            y='normalized_labour_grad_FR',
            size='normalized_GVA_grad_FR',
            hover_name='quarter'  
            )
        st.plotly_chart(fig)

        st.write("""
        This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.

        - **X-axis**: Represents the normalized employment growth in the IT sector.
        - **Y-axis**: Represents the normalized labor growth in the IT sector.
        - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
        - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
        - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.

        Hover over the bubbles to see details about the specific quarter and country data.
        """)
        fig = px.scatter(
            custom_gradients_df_with_index,  # Reset index temporarily for the plot
            x='normalized_employment_grad_FR',
            y='normalized_labour_grad_FR',
            size='normalized_GVA_grad_FR',
            hover_name='quarter',
            animation_frame= 'quarter'
            )
        st.plotly_chart(fig)

    # Tab 3: Germany (DE)
    with tab4:
        st.write("### Germany (DE)")
        
        col1, col2 = st.columns([1,2])
        
        # Column 1
        with col1:
            st.write("**ICT Employment Data**")
            plt.figure(figsize=(8, 6))
            country = 'DE'
            plt.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'ICT Employment Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of Total Employees')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)
        
            st.write("**GVA Data**")
            plt.figure(figsize=(8, 6))
            plt.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'GVA Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of GDP')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)

            st.write("**Labour Demand Data**")
            plt.figure(figsize=(8, 6))
            plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o', label=f'{country}')
            plt.title(f'Labour Demand Data for {country}')
            plt.xlabel('Quarter')
            plt.ylabel('Percentage of Total Job Advertisements Online')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)

        with col2:
            st.write("**Index**")
            # Plot the index for Germany (DE)
            plt.figure(figsize=(6, 10), dpi=150)
            plt.plot(index_data.index, index_data['DE'], marker='o', label='Germany (DE)')
            plt.title('Index for Germany (DE)')
            plt.xlabel('Quarter')
            plt.ylabel('Index Value')
            plt.xticks(rotation=45)
            plt.grid(True)
            st.pyplot(plt)

         # Temporarily add the index (quarters) as a column for hover_name
        custom_gradients_df_with_index = custom_gradients_df.reset_index().rename(columns={'index': 'quarter'})

        fig = px.scatter(
            custom_gradients_df_with_index,  # Reset index temporarily for the plot
            x='normalized_employment_grad_DE',
            y='normalized_labour_grad_DE',
            size='normalized_GVA_grad_DE',
            hover_name='quarter'  
            )
        st.plotly_chart(fig)

        st.write("""
        This animated bubble plot visualizes how the employment, labor, and Gross Value Added (GVA) metrics evolve over time for various countries.

        - **X-axis**: Represents the normalized employment growth in the IT sector.
        - **Y-axis**: Represents the normalized labor growth in the IT sector.
        - **Bubble Size**: Reflects the normalized GVA (Gross Value Added) in the IT sector for each country.
        - **Color (WILL BE)**: The color of each bubble corresponds to an index value derived from another dataset, indicating the performance or digital transformation potential of each country.
        - **Animation**: The plot is animated over time, with each frame representing a different quarter. You can see how the metrics for each country change across quarters, providing insights into trends and shifts over time.

        Hover over the bubbles to see details about the specific quarter and country data.
        """)

        fig = px.scatter(
            custom_gradients_df_with_index,  # Reset index temporarily for the plot
            x='normalized_employment_grad_DE',
            y='normalized_labour_grad_DE',
            size='normalized_GVA_grad_DE',
            hover_name='quarter',
            animation_frame= 'quarter'
            )
        st.plotly_chart(fig)
        
elif page == page4:
    
     st.title("DTPI - Top X Selected Countries")
     tabs = st.tabs([f'{title}' for title in country_titles])

     for i, country in enumerate(countries):
         with tabs[i]:
             st.write(f'Data for **{country_titles[i]}**: you can scroll and zoom into the details for the different views')
             col1, col2 = st.columns([1,2])
        
        
            # Column 1 content: ICT Employment, GVA, and Labour Demand Data
             with col1:
                st.write("**ICT Employment Data**")
                fig1, ax1 = plt.subplots(figsize=(4, 3))  # Adjust figure size
                ax1.plot(filtered_data['Employment'][country]['quarter'], filtered_data['Employment'][country]['value'], marker='o', color='grey')
                ax1.set_title(f'ICT Employment Data for {country}', fontsize=12)
                ax1.set_xlabel('Quarter', fontsize=10)
                ax1.set_ylabel('Percentage of Total Employees', fontsize=10)
                ax1.grid(True)  # Add grid to the plot
                ax1.tick_params(axis='x', rotation=45, labelsize=9)
                ax1.tick_params(axis='y', labelsize=9)
                st.pyplot(fig1)

                st.write("**Labour Demand Data**")
                fig3, ax3 = plt.subplots(figsize=(4, 3))  # Adjust figure size
                ax3.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['value'], marker='o', color='grey')
                ax3.set_title(f'Labour Demand Data for {country}', fontsize=12)
                ax3.set_xlabel('Quarter', fontsize=10)
                ax3.set_ylabel('Percentage of Total Job Advertisements Online', fontsize=10)
                ax3.grid(True)  # Add grid to the plot
                ax3.tick_params(axis='x', rotation=45, labelsize=9)
                ax3.tick_params(axis='y', labelsize=9)
                st.pyplot(fig3)

                st.write("**GVA Data**")
                fig2, ax2 = plt.subplots(figsize=(4, 3))  # Adjust figure size
                ax2.plot(filtered_data['GVA'][country]['quarter'], filtered_data['GVA'][country]['value'], marker='o', color='green')
                ax2.set_title(f'GVA Data for {country}', fontsize=12)
                ax2.set_xlabel('Quarter', fontsize=10)
                ax2.set_ylabel('Percentage of GDP', fontsize=10)
                ax2.grid(True)  # Add grid to the plot
                ax2.tick_params(axis='x', rotation=45, labelsize=9)
                ax2.tick_params(axis='y', labelsize=9)
                st.pyplot(fig2)

            # Column 2 content: Index plot and bubble chart
             with col2:
                st.write(f"**DTPI Indicator for {country}**")
                fig_index, ax_index = plt.subplots(figsize=(5, 4))  # Adjust figure size
                ax_index.plot(index_data.index, index_data[f'{country}'], marker='x', label=f'{country}', color='red')
                ax_index.set_title(f'Index for {country}', fontsize=12)
                ax_index.set_xlabel('Quarter', fontsize=10)
                ax_index.set_ylabel('Index Value', fontsize=10)
                ax_index.grid(True)  # Add grid to the plot
                ax_index.tick_params(axis='x', rotation=45, labelsize=9)
                ax_index.tick_params(axis='y', labelsize=9)
                st.pyplot(fig_index)

                # Set bubble plot dimensions to align properly
                custom_gradients_df_with_index = custom_gradients_df.reset_index().rename(columns={'index': 'quarter'})
                
                
                fig_bubble = px.scatter(
                    custom_gradients_df_with_index,
                    x=f'normalized_employment_grad_{country}',
                    y=f'normalized_labour_grad_{country}',
                    size=f'normalized_GVA_grad_{country}',
                    hover_name='quarter',
                    animation_frame='quarter',
                )

                fig_bubble.update_layout(
                    width=600,                                                                              # Adjust width to match layout
                    height=400,                                                                             # Adjust height to align with left column
                    margin=dict(l=20, r=20, t=30, b=20),                                                    # Adjust margins for better alignment
                    xaxis_title="Normalized Employment Growth",                                             # Add x-axis label
                    yaxis_title="Normalized Labour Growth",                                                 # Add y-axis label
                    font=dict(size=10),                                                                     # Set overall font size for the plot
                    title_font=dict(size=12),                                                               # Set title font size
                    title="Normalised Labour Vs Employment Growth over Quarters",
                    hoverlabel=dict(font_size=9),                                                           # Adjust hover text font size
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey', range = [-0.1,1.1]),      # Add grid to x-axis
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey', range = [-0.1,1.1]),      # Add grid to y-axis
                )

                st.plotly_chart(fig_bubble)
             
             st.write(f'**Comments for {country} DPTI Indicator**')

             highlights_per_year_quarter = description_text_by_quarter(country)
             print(f'>>> Contents for  {country}')
             print(json.dumps(highlights_per_year_quarter, indent=2))

             collapsed = False
             years = sorted(list(highlights_per_year_quarter.keys()), reverse=True)
             for year in years:
                 quarters = sorted(list(highlights_per_year_quarter[year].keys()), reverse=True)
                 for quarter in quarters:
                     if not collapsed:
                         st.markdown(f'<details open><summary>{year} {quarter}</summary>{highlights_per_year_quarter[year][quarter]}</details>', unsafe_allow_html=True, help=None)
                         collapsed = True
                     else:
                         st.markdown(f'<details><summary>{year} {quarter}</summary>{highlights_per_year_quarter[year][quarter]}</details>', unsafe_allow_html=True, help=None)