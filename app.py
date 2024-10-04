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

from text_to_print import description_text_by_quarter, load_md_overview
from sklearn.preprocessing import MinMaxScaler  # Or use StandardScaler for Z-score normalization
from data_processing import process_import_data, process_ICT_labour_import_data

# Set the page configuration at the top of the script
st.set_page_config(
    page_title="B&DT Club Digital Transformation Index",  # Optional: Give your app a title
    layout="centered"  # Using the centered layout
)

# Sidebar for navigation
page1 = "DTPI - EU27 overview"
page2 = "DTPI - Selected X countries"
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [page1, page2])


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

if page==page1:

    st.title("The DTPI - A summary for EU27 countries")

elif page == page2:
    
     st.title("DTPI - Top X Selected Countries")

    # Tab 0 is for the Overview, the rest is for selected countries
     tabs = st.tabs(['Overview'] + [f'{title}' for title in country_titles])
     i = 0
     with tabs[i]:
         st.markdown(f'{load_md_overview()}', unsafe_allow_html=True, help=None)
     
     for country in countries:
         i += 1
         with tabs[i]:
             
             st.markdown(f'### Data for **{country_titles[i-1]}**: you can scroll and zoom into the details for the different views')
             st.markdown(f'---')
             
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
                    title="Animation of Normalised Labour Vs Employment Growth over Quarters",
                    hoverlabel=dict(font_size=9),                                                           # Adjust hover text font size
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey', range = [-0.1,1.1]),      # Add grid to x-axis
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey', range = [-0.1,1.1]),      # Add grid to y-axis
                )

                st.plotly_chart(fig_bubble)
             
             st.markdown(f'---')
             st.markdown(f'### Historical Analysis and Highlights for {country} DPTI Indicator')

             highlights_per_year_quarter = description_text_by_quarter(country)
             print(f'>>> Contents for  {country}')
             print(json.dumps(highlights_per_year_quarter, indent=2))

             # Time to render the markdown contents, making visible always the last quarter from the last year
             collapsed = False
             years = sorted(list(highlights_per_year_quarter.keys()), reverse=True)
             # Going over the years, and the quarters in the year, it retrieves the contents and prepares for
             # formatting and visualisation, leveraging the markdown renderer
             for year in years:
                 quarters = sorted(list(highlights_per_year_quarter[year].keys()), reverse=True)
                 for quarter in quarters:
                     if not collapsed:
                         st.markdown(f'<details open><summary>{year} {quarter}</summary>{highlights_per_year_quarter[year][quarter]}</details>', unsafe_allow_html=True, help=None)
                         collapsed = not collapsed
                         continue
                     st.markdown(f'<details><summary>{year} {quarter}</summary>{highlights_per_year_quarter[year][quarter]}</details>', unsafe_allow_html=True, help=None)