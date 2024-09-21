import streamlit as st
import eurostat
import pandas as pd
import matplotlib.pyplot as plt
from data_processing import process_import_data, process_ICT_labour_import_data
from sklearn.preprocessing import MinMaxScaler  # Or use StandardScaler for Z-score normalization

# Normalize the data using Min-Max scaling
scaler = MinMaxScaler()

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

    # Filter GVA data for nace_r2 = 'J' and unit = 'PC_GDP' where J = ICT
    filtered_gva_data = GVA_data[(GVA_data['nace_r2'] == 'J') & 
                                 (GVA_data['unit'] == 'PC_GDP') & 
                                 (GVA_data['geo'] == 'IT') & 
                                 (GVA_data['na_item'] == 'B1G') & 
                                 (GVA_data['s_adj'] == 'NSA')]

    # Filter Employment data for nace_r2 = 'J' and unit = 'PC_TOT_PER' (ICT industry)
    filtered_employment_data = Employment_data[(Employment_data['nace_r2'] == 'J') & 
                                               (Employment_data['unit'] == 'PC_TOT_PER') & 
                                               (Employment_data['geo'] == 'IT') & 
                                               (Employment_data['na_item'] == 'EMP_DC') & 
                                               (Employment_data['s_adj'] == 'NSA')]

    filtered_labour_demand_data = Labour_demand_ICT_data[(Labour_demand_ICT_data['geo'] == 'IT') &
                                                          (Labour_demand_ICT_data['unit'] == 'PC')]


    return filtered_gva_data, filtered_employment_data, filtered_labour_demand_data

# Load the data from the cached function
filtered_gva_data, filtered_employment_data, filtered_labour_demand_data = load_data()

# Convert 'quarter' from Period to string format for proper labeling
filtered_gva_data['quarter'] = filtered_gva_data['quarter'].dt.strftime('%Y-Q%q')
filtered_employment_data['quarter'] = filtered_employment_data['quarter'].dt.strftime('%Y-Q%q')
filtered_labour_demand_data['quarter'] = filtered_labour_demand_data['quarter'].dt.strftime('%Y-Q%q')

filtered_employment_data['normalized_value'] = scaler.fit_transform(filtered_employment_data[['value']])
filtered_gva_data['normalized_value'] = scaler.fit_transform(filtered_gva_data[['value']])
filtered_labour_demand_data['normalized_value'] = scaler.fit_transform(filtered_labour_demand_data[['value']])

# Create two columns
col1, col2 = st.columns(2)

with col1:
    # Plot Employment data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_employment_data['quarter'], filtered_employment_data['value'], marker='o')
    plt.title('Employment Data for IT (Industry J)')
    plt.xlabel('Quarter')
    plt.ylabel('Percentage of Total Employees')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the Employment plot in the Streamlit app
    st.pyplot(plt)

    # Plot GVA data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_gva_data['quarter'], filtered_gva_data['value'], marker='o')
    plt.title('GVA Data for IT (Industry J)')
    plt.xlabel('Quarter')
    plt.ylabel('Percentage of GDP')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the GVA plot in the Streamlit app
    st.pyplot(plt)

    # Plot labour demand data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_labour_demand_data['quarter'], filtered_labour_demand_data['value'], marker='o')
    plt.title('Labour demand for IT (Industry J)')
    plt.xlabel('Quarter')
    plt.ylabel('Percentage of total job advertisement online')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the GVA plot in the Streamlit app
    st.pyplot(plt)

with col2:

    # Plot Employment data normalized
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_employment_data['quarter'], filtered_employment_data['normalized_value'], marker='o')
    plt.title('Employment Data for IT (Industry J) - Normalized')
    plt.xlabel('Quarter')
    plt.ylabel('Normalized Percentage of Total Employees')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the Employment plot in the Streamlit app
    st.pyplot(plt)

    # Plot Normalized GVA data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_gva_data['quarter'], filtered_gva_data['normalized_value'], marker='o')
    plt.title('GVA Data for IT (Industry J) - Normalized')
    plt.xlabel('Quarter')
    plt.ylabel('Normalized Percentage of GDP')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the GVA plot in the Streamlit app
    st.pyplot(plt)

    # Plot normalized labour demand data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_labour_demand_data['quarter'], filtered_labour_demand_data['normalized_value'], marker='o')
    plt.title('Labour demand for IT (Industry J) - Normalized')
    plt.xlabel('Quarter')
    plt.ylabel('Normalized Percentage of total job advertisement online')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the GVA plot in the Streamlit app
    st.pyplot(plt)
        

# Merge the three datasets on the 'quarter' column to align them
merged_data = pd.merge(filtered_employment_data[['quarter', 'normalized_value']], 
                       filtered_gva_data[['quarter', 'normalized_value']], 
                       on='quarter', suffixes=('_employment', '_gva'))

merged_data = pd.merge(merged_data, 
                       filtered_labour_demand_data[['quarter', 'normalized_value']], 
                       on='quarter')

# Calculate the Index after aligning the data
merged_data['Index'] = merged_data['normalized_value_employment'] * (
    merged_data['normalized_value'] + merged_data['normalized_value'])

# Now plot the Index using the aligned data
plt.figure(figsize=(10, 6))
plt.plot(merged_data['quarter'], merged_data['Index'], marker='o')
plt.title('Index')
plt.xlabel('Quarter')
plt.ylabel('[-]')
plt.xticks(rotation=45)
plt.grid(True)

# Display the Index plot in the Streamlit app
st.pyplot(plt)

