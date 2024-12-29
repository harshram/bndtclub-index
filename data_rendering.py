
# To centralise the styling via CSS
css = {
    'logo': """
        <style>
            [alt=Logo] {
            height: 5rem;
            }
        </style>
    """,
    'body': """
        <style>
            /* Adjust the width of the block-container class */
            .block-container {
                max-width: 1000px;  /* Adjust this value to control the width */
                padding-top: 3rem;
                padding-right: 1rem;
                padding-left: 1rem;
                padding-bottom: 1rem;
            }

            /* Set the background color for the entire page */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #002f6c !important;
            }

            /* Set the text color for all text elements */
            html, body, .stText, .stMarkdown, .css-10trblm, .css-1v0mbdj, .css-1cpxqw2, .css-1cpxqw2 h1, 
            .css-1cpxqw2 h2, .css-1cpxqw2 h3, .css-1v0mbdj h1, .css-1v0mbdj h2, .css-1v0mbdj h3, 
            span, div, h1, h2, h3, h4, h5, h6 {
                color: #e5e5e5 !important;
            }

            /* Styling for dropdowns */
            select, option {
                color: #544c4c !important; /* Text color for dropdown options */
                background-color: #003366 !important; /* Background color for dropdown options */
            }

            /* Table styling */
            table {
                color: #e5e5e5 !important;  /* Font color */
                border-collapse: collapse;  /* Remove space between table borders */
                width: 100%;
            }

            thead th {
                color: #e5e5e5 !important;  /* Header font color */
                border-bottom: 2px solid #e5e5e5 !important;  /* Header bottom border */
            }

            tbody td, tbody th {
                border: 1px solid #e5e5e5 !important;  /* Table cell borders */
                padding: 8px !important;  /* Add padding to improve readability */
            }

            tbody th {
                color: #e5e5e5 !important;  /* Index (first column) font color */
                background-color: #003366 !important;  /* Background color for the first column */
                text-align: left !important;  /* Align text in the index column to the left */
            }

            tbody tr:nth-child(even) {
                background-color: #003366 !important;  /* Background color for even rows */
            }

            tbody tr:nth-child(odd) {
                background-color: #002f6c !important;  /* Background color for odd rows */
            }

            /* Adjust the styling for the chosen option (selected value) */
            .st-dt.st-de.st-cu.st-du.st-dv.st-dw {
                color: #ffffff !important;  /* Text color for the selected value */
                
            }

            /* Adjust the styling for the dropdown options */
            .st-ct.st-ch.st-b4.st-c3.st-bd.st-dx.st-dy {
                color: #ffffff !important;  /* Text color for the dropdown options */
                
            }

            /* Optional: Add hover effect for better interactivity */
            .st-ct.st-ch.st-b4.st-c3.st-bd.st-dx.st-dy:hover {
                
            }
        </style>
    """
}


# Mapping table to address common labels used over and over again
data_to_plot_labels = {
    'Employment': {
        'title': 'Employment Data for IT, FR, DE (Industry J)',
        'x_label': 'Quarter',
        'y_label': 'Percentage of Total Employees'
    },
    'GVA': {
        'title': 'GVA Data for IT, FR, DE (Industry J)',
        'x_label': 'Quarter',
        'y_label': 'Percentage of GDP'
    },
    'LabourDemand': {
        'title': 'Labour Demand for IT, FR, DE (Industry J)',
        'x_label': 'Quarter',
        'y_label': 'Percentage of total job advertisement online'
    }
}

# Helper function to plot
def plot(plt, title='', x_label='', y_label=''):
    pass

# Render version 1 of the indicator
def render_version1(st, plt, countries, filtered_data):
    for k in filtered_data:
        for c in countries:
            pass

# Render version 2 of the indicator
def render_version2():
    pass

# Render version 3 of the indicator
def render_version3():
    pass

# Render version 4 of the indicator
def render_version4():
    pass

# Render version 5 of the indicator
def render_version5():
    pass

def render_qoq_analysis_markdown(highlights_text, countries):
    pass