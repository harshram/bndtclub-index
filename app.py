import streamlit as st
import eurostat
import pandas as pd
import matplotlib.pyplot as plt
from data_processing import process_import_data, process_ICT_labour_import_data
from sklearn.preprocessing import MinMaxScaler  # Or use StandardScaler for Z-score normalization

# Normalize the data using Min-Max scaling
scaler = MinMaxScaler()

# List of countries for which to process and plot data
countries = ['IT', 'FR', 'DE']  # Italy, France, and Germany

# Caching data to save time in loading data from API call
@st.cache_data
def load_data():
    # Load the raw data from Eurostat API
    GVA_data_import = eurostat.get_data_df('namq_10_a10')
    Employment_data_import = eurostat.get_data_df('namq_10_a10_e')
    Labour_demand_ICT_data_import = eurostat.get_data_df('isoc_sk_oja1')

    # Define the starting quarter for filtering data
    date_start = '2019Q4'

    # Process the raw data
    GVA_data = process_import_data(GVA_data_import, date_start)
    Employment_data = process_import_data(Employment_data_import, date_start)
    Labour_demand_ICT_data = process_ICT_labour_import_data(Labour_demand_ICT_data_import, date_start)

    return GVA_data, Employment_data, Labour_demand_ICT_data

# Load the data from the cached function
GVA_data, Employment_data, Labour_demand_ICT_data = load_data()

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

#st.write("## Index Formula:")
st.write('DTPI1: Simple, assumes equal contribution of all factors. Easy to understand but treats components as fully substitutable.')
st.latex(r'''
            DTPI_1 =  \frac{1}{3} \times GVA_{\text{norm}} \times \frac{1}{3} \text{Emp}_{\text{norm}} + \frac{1}{3} \text{Demand}_{\text{norm}}
            ''')

st.write('DTPI2: Highlights GVA’s impact with employment/demand trends. More sensitive to extreme values, emphasizing magnitude and trends.')
st.latex(r'''
    DTPI_2 = GVA_{\text{norm}} \times \left( \text{Emp}_{\text{norm}} + \text{Demand}_{\text{norm}} \right)
    ''')

st.write('DTPI3: Balances components multiplicatively, reducing extreme impacts. Reflects that all areas must perform well for higher scores.')
st.latex(r'''
    DTPI_3 = GVA_{\text{norm}} \times \left( 1 + \text{Emp}_{\text{norm}} + \text{Demand}_{\text{norm}} \right)
    ''')
st.write('Digital Transformation Potential Index (DTPI)')

# Create two columns for the plots
col1, col2, col3 = st.columns(3)


# Plot overlapping Employment, GVA, and Labour demand data for all countries
with col1:
    # Plot Employment data for all countries
    plt.figure(figsize=(15, 8))
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
    plt.figure(figsize=(15, 8))
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
    plt.figure(figsize=(15, 8))
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
    # Plot Normalized Employment data for all countries
    plt.figure(figsize=(15, 8))
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
    plt.figure(figsize=(15, 8))
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
    plt.figure(figsize=(15, 8))
    for country in countries:
        plt.plot(filtered_data['LabourDemand'][country]['quarter'], filtered_data['LabourDemand'][country]['normalized_value'], marker='o', label=f'Normalized Labour Demand - {country}')
    plt.title('Normalized Labour Demand for IT, FR, DE (Industry J)')
    plt.xlabel('Quarter')
    plt.ylabel('Normalized Percentage of total job advertisement online')
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

    temp = pd.merge(temp, 
                    filtered_data['LabourDemand'][country][['quarter', 'normalized_value']], 
                    on='quarter')

    temp['Index1'] = 0.333*temp['normalized_value_employment'] + 0.333*temp['normalized_value_gva'] + 0.333*temp['normalized_value']
    temp['Index2'] = temp['normalized_value_employment'] * (temp['normalized_value_gva'] + temp['normalized_value'])
    temp['Index3'] = temp['normalized_value_employment'] * (1 + temp['normalized_value_gva'] + temp['normalized_value'])

    temp['country'] = country
    merged_data = pd.concat([merged_data, temp])

# Display the index 1 formula before plotting


with col3:

    # Plot Index for all countries
    plt.figure(figsize=(15, 8))
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

    
    # Plot Index for all countries
    plt.figure(figsize=(15, 8))
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

 
    # Plot Index for all countries
    plt.figure(figsize=(15, 8))
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