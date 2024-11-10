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



#%%

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



from Plotting_raw_data_class import PlotWindow

if __name__ == "__main__":
    root = tk.Tk()
    'app = PlotWindow(root, start_date_plot, end_date_plot, df_raw_sump, spill_level)'
    app = PlotWindow(root, "2024-10-01", "2024-10-20", df_raw_sump=df_sump_filtered, df_rainfall=df_rainfall_filtered, df_hour_agg_flow_meter=df_hour_agg_flow_meter_filtered, spill_level=95, sump_ylim=100)
    root.mainloop()




#%%

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
import matplotlib.pyplot as plt

# Assuming df_rainfall and df_raw_flow_meter are already loaded as pandas dataframes

# Merge the two dataframes on the datetime columns
df = pd.merge(df_rainfall, df_raw_flow_meter, left_on='time_gmt_n', right_on='TimeGMT')

# Sort the dataframe by datetime
df = df.sort_values(by='time_gmt_n')

# Split the data into training and testing sets (first half for training, second half for testing)
train_size = len(df) // 2
train_df = df.iloc[:train_size]
test_df = df.iloc[train_size:]

# Prepare the input and output variables
X_train = train_df[['Intensity']].values
y_train = train_df['EValue'].values
X_test = test_df[['Intensity']].values
y_test = test_df['EValue'].values

# Scale the data
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1))
X_test_scaled = scaler_X.transform(X_test)
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1))

# Build the neural network model using sklearn's MLPRegressor
model = MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', solver='adam', max_iter=500)

# Train the model
model.fit(X_train_scaled, y_train_scaled.ravel())

# Predict on the test set
y_pred_scaled = model.predict(X_test_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))

# Plot the results
plt.figure(figsize=(14, 7))
plt.plot(df['time_gmt_n'], df['Intensity'], label='Intensity (mm/hr)', color='blue')
plt.plot(test_df['time_gmt_n'], y_test, label='Actual EValue', color='green')
plt.plot(test_df['time_gmt_n'], y_pred, label='Predicted EValue', color='red')
plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Intensity (mm/hr), Actual EValue and Predicted EValue')
plt.legend()
plt.show()
