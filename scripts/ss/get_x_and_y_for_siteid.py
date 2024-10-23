# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:47:45 2024

@author: RMCGINT
"""

import pandas as pd
import numpy as np

# Load the Excel file into a DataFrame
df_sites_list = pd.read_excel('../ww_site_info/ww_sites_list.xlsx')


# Strip any leading/trailing whitespace from column names
df_sites_list.columns = df_sites_list.columns.str.strip()

# Drop unnamed columns
df_sites_list = df_sites_list.loc[:, ~df_sites_list.columns.str.contains('^Unnamed')]



# Function to round to the nearest number ending in 500
def round_to_nearest_500(num):
    # Round to the nearest 500
    rounded = round(num / 500) * 500
    
    # Ensure the result ends in 500
    if rounded % 1000 == 0:
        rounded += 500
    
    return rounded

# Function to get X and Y values for a given SITEID and round them
def get_rounded_coordinates(site_id):
    # Filter the DataFrame for the given SITEID
    site_data = df_sites_list[df_sites_list['SITEID'] == site_id]
    print(site_data)
    
    if not site_data.empty:
        x_value = site_data['X'].values.item()  # Extract the first element and convert to a scalar
        y_value = site_data['Y'].values.item()  # Extract the first element and convert to a scalar
        
        # Ensure the values are numeric
        x_value = float(x_value)
        y_value = float(y_value)
        
        # Round the X and Y values to the nearest number ending in 500
        rounded_x = round_to_nearest_500(x_value)
        rounded_y = round_to_nearest_500(y_value)
        
        return rounded_x, rounded_y
    else:
        return None, None


# Example usage
site_id = 15468 # Replace with the actual SITEID you want to search for
rounded_x, rounded_y = get_rounded_coordinates(site_id)

if rounded_x is not None and rounded_y is not None:
    print(f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}")
else:
    print(f"SITEID {site_id} not found in the data.")
