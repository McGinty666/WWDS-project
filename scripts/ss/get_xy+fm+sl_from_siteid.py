# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:47:45 2024

@author: RMCGINT
"""

import pandas as pd
import numpy as np

# Load the Excel file into a DataFrame
df_sites_list = pd.read_excel('../ww_site_info/ww_sites_list.xlsx')
df_asset_register = pd.read_excel('../ww_site_info/edm_asset_register.xlsx', header=1)


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



# Function to get additional information for a given SITEID from the second DataFrame
def get_sump_analogue(site_id):
    # Filter the DataFrame for the given SITEID
    asset_data = df_asset_register[df_asset_register['Site ID'] == site_id]
    
    if not asset_data.empty:
        analogue_server = asset_data['Analogue Server'].values.item()
        analogue_signal = asset_data['Analogue Signal'].values.item()
        spill_mm = asset_data['Spill (mm)'].values.item()
        pre_spill_mm = asset_data['Pre-Spill (mm)'].values.item()
        
        return analogue_server, analogue_signal, spill_mm, pre_spill_mm
    else:
        return None, None, None, None

# Example usage
site_id = 15468  # Replace with the actual SITEID you want to search for
rounded_x, rounded_y = get_rounded_coordinates(site_id)

if rounded_x is not None and rounded_y is not None:
    print(f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}")
else:
    print(f"SITEID {site_id} not found in the data.")

analogue_server, analogue_signal, spill_mm, pre_spill_mm = get_sump_analogue(site_id)

if analogue_server is not None and analogue_signal is not None:
    print(f"Additional information for SITEID {site_id}:")
    print(f"Analogue Server: {analogue_server}")
    print(f"Analogue Signal: {analogue_signal}")
    print(f"Spill(mm): {spill_mm}")
    print(f"Pre-Spill (mm): {pre_spill_mm}")
else:
    print(f"SITEID {site_id} not found in the asset register data.")
    
    
if 'Site ID' in df_asset_register.columns:
    print("Site ID column found.")
else:
    print("Site ID column not found.")
   