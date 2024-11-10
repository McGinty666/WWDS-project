# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 21:44:13 2024

@author: RMCGINT
"""

import sqlalchemy
import pyodbc
import pandas as pd
import re
from DAL_Class_1 import DAL
import processing_functions
from datetime import datetime
from site_information_class import SiteDataProcessor
import tkinter as tk
from tkinter import simpledialog, scrolledtext 
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import math
from Class_tkinter import SiteInformationApp  # Assuming your class is in a file named site_information_app.py

#%%
if __name__ == "__main__":
    root = tk.Tk()
    app = SiteInformationApp(root)
    root.mainloop()
    # Access the DataFrame after the main loop
    df_spill_hours = app.df_spill_hours
    df_rainfall = app.df_rainfall_global
    df_raw_sump = app.df_raw_sump_global
    df_hour_agg_flow_meter = app.df_hour_agg_flow_meter_global
    df_raw_flow_meter = app.df_raw_flow_meter_global
    start_date_downloaded = app.start_date_global
    end_date_downloaded = app.end_date_global
    site_id_selected = app.site_id



#%%



import os
import pandas as pd



# Define file paths
file_paths = {
    #"df_spill_hours": "../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_spill_hours.xlsx",
    "df_rainfall": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_rainfall.xlsx",
    "df_raw_sump": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}df_raw_sump.xlsx",
    "df_hour_agg_flow_meter": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}df_hour_agg_flow_meter.xlsx",
    "df_raw_flow_meter": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_raw_flow_meter.xlsx"
}

# Function to save dataframes to xlsx files
def save_dataframes(**kwargs):
    for name, df in kwargs.items():
        file_path = file_paths.get(name)
        if file_path:
            df.to_excel(file_path, index=False)
            print(f"{name} saved to {file_path}")

# Example usage:
# Assuming the dataframes are already defined and available as variables
# df_spill_hours, df_rainfall, df_raw_sump, df_hour_agg_flow_meter, df_raw_flow_meter

# Save the dataframes
save_dataframes(
    #df_spill_hours=df_spill_hours,
    df_rainfall=df_rainfall,
    df_raw_sump=df_raw_sump,
    df_hour_agg_flow_meter=df_hour_agg_flow_meter,
    df_raw_flow_meter=df_raw_flow_meter
)

#%%
# Define file paths
'''

import os
import pandas as pd


file_paths = {
    "df_spill_hours": f"../data/raw/df_spill_hours.xlsx",
    "df_rainfall": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_rainfall.xlsx",
    "df_raw_sump": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_raw_sump.xlsx",
    "df_hour_agg_flow_meter": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_hour_agg_flow_meter.xlsx",
    "df_raw_flow_meter": f"../data/raw/site_id{site_id_selected}_{start_date_downloaded}_to_{end_date_downloaded}_df_raw_flow_meter.xlsx"
}

# Function to load dataframes from xlsx files if they exist
def load_dataframes():
    dataframes = {}
    for name, file_path in file_paths.items():
        if os.path.exists(file_path):
            dataframes[name] = pd.read_excel(file_path)
            print(f"{name} loaded from {file_path}")
        else:
            dataframes[name] = None
            print(f"{file_path} does not exist. {name} not loaded.")
    return dataframes

# Load the dataframes if they exist
loaded_dataframes = load_dataframes()

# Access the loaded dataframes
df_spill_hours = loaded_dataframes["df_spill_hours"]
df_rainfall = loaded_dataframes["df_rainfall"]
df_raw_sump = loaded_dataframes["df_raw_sump"]
df_hour_agg_flow_meter = loaded_dataframes["df_hour_agg_flow_meter"]
df_raw_flow_meter = loaded_dataframes["df_raw_flow_meter"]

'''

#%%
'''
start_date_plot = start_date_downloaded
end_date_plot = end_date_downloaded
df_sump_filtered = df_raw_sump
df_rainfall_filtered = df_rainfall
df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter
'''
import numpy as np

start_date_plot = '01-10-2024'
end_date_plot = '10-10-2024'
df_sump_filtered = df_raw_sump
df_sump_filtered = df_sump_filtered.sort_values(by="TimeGMT")


#df_rainfall = df_rainfall_loaded
# Create an empty dataframe to store the sorted results
df_rainfall_sorted = pd.DataFrame(columns=['ReadingDate', 'Intensity(mm/hr)', 'Easting', 'Northing'])
# Get unique combinations of Easting and Northing
unique_combinations = df_rainfall[['Easting', 'Northing']].drop_duplicates()


# Create a pivot table with ReadingDate as index and Easting-Northing combinations as columns
df_pivot = df_rainfall.pivot_table(index='ReadingDate', 
                                   columns=['Easting', 'Northing'], 
                                   values='Intensity(mm/hr)', 
                                   aggfunc='first')

# Flatten the multi-level columns
df_pivot.columns = [f'Intensity_{easting}_{northing} (mm/h)' for easting, northing in df_pivot.columns]

# Reset index to make ReadingDate a column again
df_pivot.reset_index(inplace=True)

# Convert all columns except 'ReadingDate' to numeric, forcing errors to NaN
df_pivot.iloc[:, 1:] = df_pivot.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# Calculate the median intensity
# Calculate the median intensity, accepting NaN values
df_pivot['Median_Intensity(mm/hr)'] = df_pivot.iloc[:, 1:].median(axis=1, skipna=True)

# Display the new dataframe
print(df_pivot.head(10))



#Not sure if this is needed? assuming the rainfall is in local time?
# Convert the ReadingDate to datetime and localize to 'Europe/London'
df_rainfall = df_pivot
df_rainfall['Intensity(mm/hr)'] = df_rainfall['Median_Intensity(mm/hr)']*12

df_rainfall['timestamp'] = pd.to_datetime(df_rainfall['ReadingDate'], format='%Y%m%d%H%M')
df_rainfall = df_rainfall.sort_values(by="timestamp")

# Localize the 'timestamp' column to 'Europe/London'
df_rainfall['timestamp'] = df_rainfall['timestamp'].dt.tz_localize('Europe/London')

# Convert the 'timestamp' column to UTC
df_rainfall['time_gmt'] = df_rainfall['timestamp'].dt.tz_convert('UTC')
df_rainfall['time_gmt_n'] = df_rainfall['time_gmt'].dt.tz_localize(None)

df_rainfall_filtered = df_rainfall.sort_values(by="time_gmt_n")




df_hour_agg_flow_meter = df_hour_agg_flow_meter


df_hour_agg_flow_meter['TimeGMT'] = pd.to_datetime(
    df_hour_agg_flow_meter['Year'].astype(str) + '-' +
    df_hour_agg_flow_meter['Month'].astype(str) + '-' +
    df_hour_agg_flow_meter['Day'].astype(str) + ' ' +
    df_hour_agg_flow_meter['Hour'].astype(str) + ':00:00'
)
df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter.sort_values(by="TimeGMT")
# Drop unnecessary columns
df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter_filtered.drop(columns=['stddev_EValue', 'count', 'DbAddr'])



spill_level = 95

#%%

import pandas as pd

# Assuming your existing DataFrame is named df_rainfall_filtered

# Fill missing values in 'Intensity(mm/hr)' with 0
df_rainfall_filtered['Intensity(mm/hr)'] = df_rainfall_filtered['Intensity(mm/hr)'].fillna(0)

# Resample to hourly frequency and sum the Intensity(mm/hr) values, then divide by 12
df_rainfall_hour_agg = df_rainfall_filtered.resample('h').sum(numeric_only=True) / 12

# Reset the index to make 'time_gmt_n' a column again
df_rainfall_hour_agg.reset_index(inplace=True)

# Display the resulting DataFrame
print(df_rainfall_hour_agg)



#%%



from Plotting_raw_data_class import PlotWindow

if __name__ == "__main__":
    root = tk.Tk()
    'app = PlotWindow(root, start_date_plot, end_date_plot, df_raw_sump, spill_level)'
    app = PlotWindow(root, "2024-10-01", "2024-10-20", df_raw_sump=df_sump_filtered, df_rainfall=df_rainfall_hour_agg, df_hour_agg_flow_meter=df_hour_agg_flow_meter_filtered, spill_level=95, sump_ylim=100)
    root.mainloop()




#%%

