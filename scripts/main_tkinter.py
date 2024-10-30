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
import tkinter as tk
from Class_tkinter import SiteInformationApp  # Assuming your class is in a file named site_information_app.py

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

#%%
import os
import pandas as pd



# Define file paths
file_paths = {
    #"df_spill_hours": "../data/raw/df_spill_hours.xlsx",
    "df_rainfall": "../data/raw/df_rainfall.xlsx",
    "df_raw_sump": "../data/raw/df_raw_sump.xlsx",
    "df_hour_agg_flow_meter": "../data/raw/df_hour_agg_flow_meter.xlsx",
    "df_raw_flow_meter": "../data/raw/df_raw_flow_meter.xlsx"
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
file_paths = {
    "df_spill_hours": "../data/raw/df_spill_hours.xlsx",
    "df_rainfall": "../data/raw/df_rainfall.xlsx",
    "df_raw_sump": "../data/raw/df_raw_sump.xlsx",
    "df_hour_agg_flow_meter": "../data/raw/df_hour_agg_flow_meter.xlsx",
    "df_raw_flow_meter": "../data/raw/df_raw_flow_meter.xlsx"
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
df_spill_hours_loaded = loaded_dataframes["df_spill_hours"]
df_rainfall_loaded = loaded_dataframes["df_rainfall"]
df_raw_sump_loaded = loaded_dataframes["df_raw_sump"]
df_hour_agg_flow_meter_loaded = loaded_dataframes["df_hour_agg_flow_meter"]
df_raw_flow_meter_loaded = loaded_dataframes["df_raw_flow_meter"]
'''


#%%

start_date_plot = start_date_downloaded
end_date_plot = end_date_downloaded
df_sump_filtered = df_raw_sump
df_rainfall_filtered = df_rainfall
df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter


#Not sure if this is needed? assuming the rainfall is in local time?
# Convert the ReadingDate to datetime and localize to 'Europe/London'
df_rainfall['timestamp'] = pd.to_datetime(df_rainfall['ReadingDate'], format='%Y%m%d%H%M')
df_rainfall = df_rainfall.sort_values(by="timestamp")

# Localize the 'timestamp' column to 'Europe/London'
df_rainfall['timestamp'] = df_rainfall['timestamp'].dt.tz_localize('Europe/London')

# Convert the 'timestamp' column to UTC
df_rainfall['time_gmt'] = df_rainfall['timestamp'].dt.tz_convert('UTC')
df_rainfall['time_gmt_n'] = df_rainfall['time_gmt'].dt.tz_localize(None)




spill_level = 95
#%%



from Plotting_raw_data_class import PlotWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotWindow(root, start_date_plot, end_date_plot, df_raw_sump, df_rainfall, df_hour_agg_flow_meter)
    root.mainloop()




#%%

