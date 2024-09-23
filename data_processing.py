import pandas as pd

def rename_geo_cols(input_df):
    # Rename the column since it only contains geographic information
    if 'geo\\TIME_PERIOD' in input_df.columns:
        input_df.rename(columns={'geo\\TIME_PERIOD': 'geo'}, inplace=True)

def process_import_data(input_df, date):
    rename_geo_cols(input_df)

    # Melt the DataFrame to convert time columns into rows
    input_df_melted = pd.melt(input_df, id_vars=['freq', 'unit','nace_r2','s_adj','na_item','geo'], var_name='time', value_name='value')
    input_df_melted['quarter'] = pd.PeriodIndex(input_df_melted['time'], freq='Q')
    output = input_df_melted[(input_df_melted['quarter'] >= date)]
    output = output.drop(columns=['time','freq'])

    return output

def process_ICT_labour_import_data(input_df, date):
    rename_geo_cols(input_df)
    
    # Melt the DataFrame to convert time columns into rows
    input_df = input_df.drop(columns = ['freq'])
    input_df_melted = pd.melt(input_df, id_vars=['unit','geo'], var_name='time', value_name='value')
    input_df_melted['quarter'] = pd.PeriodIndex(input_df_melted['time'], freq='Q')
    output = input_df_melted[(input_df_melted['quarter'] >= date)]

    return output

