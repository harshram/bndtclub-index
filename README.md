# bndt-indicator

# Overview

This Streamlit app calculates and visualizes the Digital Transformation Potential Index (DTPI) for selected European countries. The app fetches data from Eurostat, processes it, and presents both raw and normalized values of ICT-related metrics such as Gross Value Added (GVA), Employment, and Labor Demand. It also computes five variations of the DTPI based on different combinations of these metrics.

## Data Sources
The app pulls the following datasets from Eurostat:

## Gross Value Added (GVA) data (namq_10_a10)
Employment data (namq_10_a10_e)
ICT Labor Demand data (isoc_sk_oja1)
App Features
Raw and Normalized Data Visualization:

## About the App

The app provides two-column side-by-side plots for Employment, GVA, and Labor Demand across Italy, France, and Germany.
It visualizes both the original data and its normalized versions for easier comparison.
Digital Transformation Potential Index (DTPI):

The app computes five variations of the DTPI based on different combinations of GVA, Employment, and Labor Demand. These indices highlight different aspects of digital transformation efficiency and labor demand trends.
Each index is plotted over time for the three countries.
Index Explanations:

The app includes detailed explanations of each index, discussing the methodology behind the calculations (e.g., the use of logarithmic transformations, normalization, and efficiency scaling).
Country-Specific Trends:

The app provides a textual analysis of the DTPI trends for Italy, France, and Germany, explaining the behavior of each country's digital transformation index over time.
How It Works
Data Loading and Processing:

The data is pulled from Eurostat using the eurostat Python package.
Custom functions (process_import_data and process_ICT_labour_import_data) filter and process the data to prepare it for analysis.
Min-Max scaling is used to normalize the data for comparability across countries.
Plotting:

The app uses matplotlib to create time series plots of both the raw and normalized data.
It also calculates and plots the various indices to show how GVA, Employment, and Labor Demand evolve over time.
Index Calculations:

## Index Alternatives

DTPI1: Assumes equal contributions from all factors.
DTPI2: Highlights the impact of GVA with employment and demand trends.
DTPI3: Balances components multiplicatively.
DTPI4: Scales GVA by employment, incorporating changes in labor demand.
DTPI5: Uses logarithmic scaling to balance GVA and employment while considering labor demand trends.
Setup Instructions

# Dependencies:

Streamlit
Eurostat API
Pandas
Matplotlib
Scikit-learn
Installation: Install the required Python libraries using pip:

```bash
# To install the dependencies
pip install streamlit eurostat pandas matplotlib scikit-learn
# Running the App: To run the app locally, use the following commmand
streamlit run app.py
```

## Customization
The app can be easily extended to include other countries or additional metrics by modifying the countries list or the Eurostat dataset codes.
Acknowledgments

The app uses publicly available datasets from Eurostat to provide insights into the digital transformation potential of European countries. Special thanks to the developers of the Eurostat API and the data processing libraries used in the app.