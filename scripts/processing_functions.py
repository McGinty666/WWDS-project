# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 15:53:46 2024

@author: RMCGINT
"""



import sqlalchemy
import pyodbc
import pandas as pd
import re
from DAL_Class_1 import DAL
from datetime import datetime
import matplotlib.pyplot as plt
from datetime import timedelta


def read_queries(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    queries = content.split('-- ')
    query_dict = {}
    for query in queries:
        if query.strip():
            lines = query.split('\n', 1)
            if len(lines) == 2:
                query_name, query_sql = lines
                query_dict[query_name.strip()] = query_sql.strip()
    return query_dict

def execute_query_and_return_df_site_info(connection_name, query):
    with DAL(connection_name, 17) as connection:
        if connection.connection is None:
            print(f"Failed to establish connection to {connection_name}")
            return None
        else:
            ret = connection.query(query)
            df = pd.DataFrame(ret)
            return df


'''
def execute_query_and_return_df(connection_name, query):
    with DAL(connection_name, 17) as connection:
        if connection.connection is None:
            print(f"Failed to establish connection to {connection_name}")
            return None
        else:
            ret = connection.query(query)
            df = pd.DataFrame(ret)

            # Extract the first element from tuple column names
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            if 'TimeGMT' in df.columns:
                df['TimeGMT'] = pd.to_datetime(df['TimeGMT']).dt.tz_localize(None)
            return df
'''
def execute_query_and_return_df(start_date, end_date, connection_name, query):
    with DAL(connection_name, 17) as connection:
        if connection.connection is None:
            print(f"Failed to establish connection to {connection_name}")
            return None
        else:
            ret = connection.query(query)
            df = pd.DataFrame(ret)

            # Extract the first element from tuple column names
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            if 'TimeGMT' in df.columns:
                df['TimeGMT'] = pd.to_datetime(df['TimeGMT'], utc=True).dt.tz_localize(None)
            return df


def plot_rainfall_and_sump_level(start_time, end_time):
    # Convert start and end times to datetime
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # Filter the dataframes based on the specified time interval
    df_sump_filtered = df_raw_sump[(df_raw_sump["TimeGMT"] >= start_time) & (df_raw_sump["TimeGMT"] <= end_time)]
    df_rainfall_filtered = df_rainfall[(df_rainfall["timestamp"] >= start_time) & (df_rainfall["timestamp"] <= end_time)]

    # Sort the filtered dataframes by their respective time columns
    df_sump_filtered = df_sump_filtered.sort_values(by="TimeGMT")
    df_rainfall_filtered = df_rainfall_filtered.sort_values(by="timestamp")

    # Create a figure and axis objects
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot sump level on the first y-axis
    ax1.plot(df_sump_filtered["TimeGMT"], df_sump_filtered["EValue"], color='green', label='Sump Level')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Sump Level', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    # Create a second y-axis for rainfall
    ax2 = ax1.twinx()
    ax2.plot(df_rainfall_filtered["timestamp"], df_rainfall_filtered["Intensity(mm/hr)"], color='blue', label='Rainfall')
    ax2.set_ylabel('Rainfall intensity (mm/h)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Add title and grid
    plt.title('Rainfall and Sump Level Over Time')
    fig.tight_layout()
    plt.grid(True)

    # Show the plot
    plt.show()

def plot_rainfall_mean_agg_flow_meter_and_raw_sump_level(start_time, end_time, df_raw_sump, df_rainfall, df_hour_agg_flow_meter, spill_level=None, sump_ylim=None):
    # Convert start and end times to datetime
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # Filter the dataframes based on the specified time interval
    df_sump_filtered = df_raw_sump[(df_raw_sump["TimeGMT"] >= start_time) & (df_raw_sump["TimeGMT"] <= end_time)]
    df_rainfall_filtered = df_rainfall[(df_rainfall["time_gmt_n"] >= start_time) & (df_rainfall["time_gmt_n"] <= end_time)]
    df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter[
        (pd.to_datetime(df_hour_agg_flow_meter["Year"].astype(str) + '-' + df_hour_agg_flow_meter["Month"].astype(str) + '-' + df_hour_agg_flow_meter["Day"].astype(str) + ' ' + df_hour_agg_flow_meter["Hour"].astype(str) + ':00:00') >= start_time) & 
        (pd.to_datetime(df_hour_agg_flow_meter["Year"].astype(str) + '-' + df_hour_agg_flow_meter["Month"].astype(str) + '-' + df_hour_agg_flow_meter["Day"].astype(str) + ' ' + df_hour_agg_flow_meter["Hour"].astype(str) + ':00:00') <= end_time)
    ]

    # Sort the filtered dataframes by their respective time columns
    df_sump_filtered = df_sump_filtered.sort_values(by="TimeGMT")
    df_rainfall_filtered = df_rainfall_filtered.sort_values(by="time_gmt_n")
    df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter_filtered.sort_values(by=["Year", "Month", "Day", "Hour"])

    # Create a figure and axis objects
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot sump level on the first y-axis
    ax1.plot(df_sump_filtered["TimeGMT"], df_sump_filtered["EValue"], color='green', label='Sump Level')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Sump Level', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    # Apply user-defined axis range if provided
    if sump_ylim:
        ax1.set_ylim(sump_ylim)

    # Add horizontal line for spill level if provided
    if spill_level is not None and isinstance(spill_level, (int, float)):
        ax1.axhline(y=spill_level, color='green', linestyle='--', label='Spill Level')

    # Create a second y-axis for rainfall
    ax2 = ax1.twinx()
    ax2.bar(df_rainfall_filtered["time_gmt_n"], df_rainfall_filtered["Intensity(mm/hr)"], color='blue', label='Rainfall', width=0.01)
    ax2.set_ylabel('Rainfall intensity (mm/h)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.invert_yaxis()  # Reverse the y-axis for rainfall

    # Create a third y-axis for meanEValue
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))  # Offset the third axis to the right
    ax3.plot(
        pd.to_datetime(df_hour_agg_flow_meter_filtered["Year"].astype(str) + '-' + df_hour_agg_flow_meter_filtered["Month"].astype(str) + '-' + df_hour_agg_flow_meter_filtered["Day"].astype(str) + ' ' + df_hour_agg_flow_meter_filtered["Hour"].astype(str) + ':00:00'), 
        df_hour_agg_flow_meter_filtered["meanEValue"], color='red', label='Mean EValue'
    )
    ax3.set_ylabel('Mean EValue flow meter', color='red')
    ax3.tick_params(axis='y', labelcolor='red')

    # Add title and remove horizontal grid lines
    plt.title(f'Nearby Rainfall, Sump Level, and Mean EValue flow meter from {start_time} to {end_time}')
    ax1.grid(False)  # Remove horizontal grid lines from the first y-axis
    ax2.grid(False)  # Remove horizontal grid lines from the second y-axis
    ax3.grid(False)  # Remove horizontal grid lines from the third y-axis

    fig.tight_layout()

    # Show the plot
    plt.show()
    


def update_plot(pan_direction):
    global start_time_plot, end_time_plot
    if pan_direction == 'left':
        start_time_plot = pd.to_datetime(start_time_plot) - pan_interval
        end_time_plot = pd.to_datetime(end_time_plot) - pan_interval
    elif pan_direction == 'right':
        start_time_plot = pd.to_datetime(start_time_plot) + pan_interval
        end_time_plot = pd.to_datetime(end_time_plot) + pan_interval
    # Clear the previous plot
    clear_output(wait=True)
    # Display buttons again after clearing output
    display(pan_left_button, pan_right_button)
    # Plot the updated graph
    plot_rainfall_and_sump_level(start_time_plot, end_time_plot)

#used in the early colab version using the analogues and adding a massk to say if the threshold was exceeded
def count_exceedance_instances(df):
    count = 0
    in_block = False
    block_start_time = None
# count the number of exceedances according to the EA 12/24 spill counting method
    for index, row in df.iterrows():
        if row["threshold_exceeded"]:
            if not in_block:
                # Start a new block
                in_block = True
                block_start_time = row["date_hour"]
                count += 1
            elif (row["date_hour"] - block_start_time) >= timedelta(hours=12):
                # Continue counting in 24-hour blocks
                if (row["date_hour"] - block_start_time) >= timedelta(hours=24):
                    count += 1
                    block_start_time = row["date_hour"]
        else:
            if in_block and (row["date_hour"] - block_start_time) >= timedelta(hours=24):
                # End the block if there is a 24-hour period with no exceedance
                in_block = False
    return count



def process_spill_hours(df_spill_hours):
    # Convert spill_hours to datetime
    df_spill_hours['spill_hours'] = pd.to_datetime(df_spill_hours['spill_hours'], format='%Y-%m-%d-%H')
    
    # Identify the start of spill events
    df_spill_hours['start_of_spill_event'] = (df_spill_hours['spill_hours'].diff() >= pd.Timedelta(hours=24)) | (df_spill_hours['spill_hours'].diff().isna())
    
    # Initialize the spill_event_duration column
    df_spill_hours['spill_event_duration'] = 0
    
    # Variable to keep track of the running total of hours
    running_total = 0
    
    # Iterate through the DataFrame
    for i in range(len(df_spill_hours)):
        if df_spill_hours.loc[i, 'start_of_spill_event']:
            running_total = 0  # Reset the running total
        running_total += 1  # Increment the running total by 1 hour
        df_spill_hours.loc[i, 'spill_event_duration'] = running_total
    
    # Initialize the spill_event_id column with NaN values
    df_spill_hours['spill_event_id'] = pd.NA
    
    # Set the first value of spill_event_id to 1 explicitly
    df_spill_hours.loc[0, 'spill_event_id'] = 1
    
    # Variable to keep track of the spill event ID
    spill_event_id = 1
    
    # Iterate through the DataFrame for spill_event_id starting from the second row
    for i in range(1, len(df_spill_hours)):
        if df_spill_hours.loc[i, 'start_of_spill_event']:
            spill_event_id += 1  # Increment the spill event ID if start_of_spill_event is True
        df_spill_hours.loc[i, 'spill_event_id'] = spill_event_id
    
    # Initialize the EA_12_24_counter column
    df_spill_hours['EA_12_24_counter'] = 1
    
    # Variable to keep track of the counter
    counter = 1
    
    # Iterate through the DataFrame for EA_12_24_counter
    for i in range(1, len(df_spill_hours)):
        if df_spill_hours.loc[i, 'start_of_spill_event']:
            counter += 1  # Increment the counter if start_of_spill_event is True
        elif df_spill_hours.loc[i, 'spill_event_duration'] >= 12 and df_spill_hours.loc[i - 1, 'spill_event_duration'] < 12:
            counter += 1  # Increment the counter if 12 hours have elapsed since start_of_spill_event was True
        elif df_spill_hours.loc[i, 'spill_event_duration'] % 24 == 0:
            counter += 1  # Increment the counter every 24 hours after the initial 12 hours
        df_spill_hours.loc[i, 'EA_12_24_counter'] = counter
    
    return df_spill_hours


def get_spill_block_periods(df):
    # Initialize an empty list to store the results
    results = []

    # Get unique values of spill_event_id
    unique_counters = df['spill_event_id'].unique()

    # Iterate over each unique counter
    for counter in unique_counters:
        # Filter rows with the current counter value
        counter_rows = df[df['spill_event_id'] == counter]
        
        # Convert 'spill_hours' to string and get the start_date and end_date for the current counter
        start_date = str(counter_rows['spill_hours'].iloc[0]).split()[0]
        end_date = str(counter_rows['spill_hours'].iloc[-1]).split()[0]
        
        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Subtract one day from start_date and add one day to end_date
        start_date -= timedelta(days=1)
        end_date += timedelta(days=1)
        
        # Append the result to the list
        results.append({'spill_event_id': counter, 'start_date': start_date.strftime('%Y-%m-%d'), 'end_date': end_date.strftime('%Y-%m-%d')})

    # Convert the results list to a DataFrame
    df_spill_block_periods = pd.DataFrame(results)
    
    return df_spill_block_periods

df_raw_sump_list = []
df_raw_flow_meter_list = []
df_rainfall_list = []
df_hour_agg_flow_meter_list = []
df_daily_agg_sump_list = []


def load_dataframes_from_raw(site_id, start_date_str, end_date_str):
    df_raw_sump = None
    df_raw_flow_meter = None
    df_rainfall = None
    df_hour_agg_flow_meter = None
    df_daily_agg_sump = None

    try:
        df_raw_sump = pd.read_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_sump.xlsx')
        print("Loaded df_raw_sump from xlsx file.")
    except FileNotFoundError:
        print("df_raw_sump xlsx file not found.")

    try:
        df_raw_flow_meter = pd.read_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_flow_meter.xlsx')
        print("Loaded df_raw_flow_meter from xlsx file.")
    except FileNotFoundError:
        print("df_raw_flow_meter xlsx file not found.")

    try:
        df_rainfall = pd.read_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_rainfall.xlsx')
        print("Loaded df_rainfall from xlsx file.")
    except FileNotFoundError:
        print("df_rainfall xlsx file not found.")

    try:
        df_hour_agg_flow_meter = pd.read_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_hour_agg_flow_meter.xlsx')
        print("Loaded df_hour_agg_flow_meter from xlsx file.")
    except FileNotFoundError:
        print("df_hour_agg_flow_meter xlsx file not found.")

    try:
        df_daily_agg_sump = pd.read_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_daily_agg_sump.xlsx')
        print("Loaded df_daily_agg_sump from xlsx file.")
    except FileNotFoundError:
        print("df_daily_agg_sump xlsx file not found.")

    return df_raw_sump, df_raw_flow_meter, df_rainfall, df_hour_agg_flow_meter, df_daily_agg_sump

def plot_meanEValue(df):
    """
    Plots 'meanEValue' against 'Hour' with a different line for each 'Day' in the given dataframe.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing the data with columns 'Hour', 'DbAddr', 'count', 'meanEValue', 
                       'stddev_EValue', 'Year', 'Month', 'Day'
    """
    plt.figure(figsize=(10,6))
    for day in df['Day'].unique():
        day_data = df[df['Day'] == day]
        plt.plot(day_data['Hour'], day_data['meanEValue'], label=f'Day {day}')

    plt.xlabel('Hour')
    plt.ylabel('meanEValue')
    plt.title('meanEValue against Hour with a different line for each Day')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
    
def process_rainfall_data(df_rainfall_loaded):
    # Create an empty dataframe to store the sorted results
    df_rainfall_sorted = pd.DataFrame(columns=['ReadingDate', 'Intensity(mm/hr)', 'Easting', 'Northing'])
    
    # Get unique combinations of Easting and Northing
    unique_combinations = df_rainfall_loaded[['Easting', 'Northing']].drop_duplicates()

    # Create a pivot table with ReadingDate as index and Easting-Northing combinations as columns
    df_pivot = df_rainfall_loaded.pivot_table(index='ReadingDate', 
                                              columns=['Easting', 'Northing'], 
                                              values='Intensity(mm/hr)', 
                                              aggfunc='first')

    # Flatten the multi-level columns
    df_pivot.columns = [f'Intensity_{easting}_{northing} (mm/h)' for easting, northing in df_pivot.columns]

    # Reset index to make ReadingDate a column again
    df_pivot.reset_index(inplace=True)

    # Convert all columns except 'ReadingDate' to numeric, forcing errors to NaN
    df_pivot.iloc[:, 1:] = df_pivot.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

    # Calculate the median intensity, accepting NaN values
    df_pivot['Median_Intensity(mm/hr)'] = df_pivot.iloc[:, 1:].median(axis=1, skipna=True)

    # Convert the ReadingDate to datetime and localize to 'Europe/London'
    df_rainfall = df_pivot
    df_rainfall['Intensity(mm/hr)'] = df_rainfall['Median_Intensity(mm/hr)'] * 12

    df_rainfall['timestamp'] = pd.to_datetime(df_rainfall['ReadingDate'], format='%Y%m%d%H%M')
    df_rainfall = df_rainfall.sort_values(by="timestamp")

    # Localize the 'timestamp' column to 'Europe/London'
    df_rainfall['timestamp'] = df_rainfall['timestamp'].dt.tz_localize('Europe/London', ambiguous=True)


    # Convert the 'timestamp' column to UTC
    df_rainfall['time_gmt'] = df_rainfall['timestamp'].dt.tz_convert('UTC')
    df_rainfall['time_gmt_n'] = df_rainfall['time_gmt'].dt.tz_localize(None)

    df_rainfall_filtered = df_rainfall.sort_values(by="time_gmt_n")

    # Convert 'time_gmt_n' column to datetime
    df_rainfall_filtered['time_gmt_n'] = pd.to_datetime(df_rainfall_filtered['time_gmt_n'])

    # Set 'time_gmt_n' as the index
    df_rainfall_filtered.set_index('time_gmt_n', inplace=True)

    # Fill missing values in 'Intensity(mm/hr)' with 0 and handle downcasting
    df_rainfall_filtered['Intensity(mm/hr)'] = df_rainfall_filtered['Intensity(mm/hr)'].fillna(0).infer_objects(copy=False)

    # Resample to hourly frequency and sum the Intensity(mm/hr) values, then divide by 12
    df_rainfall_hour_agg = df_rainfall_filtered.resample('H').sum(numeric_only=True) / 12

    # Reset the index to make 'time_gmt_n' a column again
    df_rainfall_hour_agg.reset_index(inplace=True)
    
    return df_rainfall_hour_agg



def transform_flow_meter_data(df_hour_agg_flow_meter):
    # Create the 'TimeGMT' column by combining Year, Month, Day, and Hour columns
    df_hour_agg_flow_meter['TimeGMT'] = pd.to_datetime(
        df_hour_agg_flow_meter['Year'].astype(str) + '-' +
        df_hour_agg_flow_meter['Month'].astype(str) + '-' +
        df_hour_agg_flow_meter['Day'].astype(str) + ' ' +
        df_hour_agg_flow_meter['Hour'].astype(str) + ':00:00'
    )
    
    # Sort the dataframe by 'TimeGMT'
    df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter.sort_values(by="TimeGMT")
    
    # Drop unnecessary columns
    df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter_filtered.drop(columns=['stddev_EValue', 'count', 'DbAddr'])
    
    return df_hour_agg_flow_meter_filtered
#%%

'''
import matplotlib.pyplot as plt


df_spill_hours['spill_hours'] = pd.to_datetime(df_spill_hours['spill_hours'], format='%Y-%m-%d-%H')

# Add columns for the Month and Year
df_spill_hours['Month'] = df_spill_hours['spill_hours'].dt.month
df_spill_hours['Year'] = df_spill_hours['spill_hours'].dt.year

# Create a new column 'start_of_spill'
df_spill_hours['start_of_spill'] = df_spill_hours['spill_hours'].diff() != pd.Timedelta(hours=1)

# Create a new column 'spill_id' which increases by 1 every time there is a start of spill
df_spill_hours['spill_id'] = df_spill_hours['start_of_spill'].cumsum()

# Create a new column 'spill_duration' which increases with each row after a spill start
df_spill_hours['spill_duration'] = df_spill_hours.groupby('spill_id').cumcount()

# Define seasons
seasons = {
    "Winter": [12, 1, 2],
    "Spring": [3, 4, 5],
    "Summer": [6, 7, 8],
    "Autumn": [9, 10, 11]
}

# Define colors for each year
colors = {
    2024: 'blue',
    2025: 'green',
    2026: 'red',
    2027: 'purple'
}

# Create subplots for each season in quadrants of an overall plot
fig, axs = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
fig.suptitle('Spill Duration Histograms by Season')

# Plot each season in its respective quadrant
for ax, (season, months) in zip(axs.flatten(), seasons.items()):
    season_data = df_spill_hours[df_spill_hours['Month'].isin(months)]
    for year in season_data['Year'].unique():
        year_data = season_data[season_data['Year'] == year]
        ax.hist(year_data['spill_duration'].dropna(), bins=range(0, int(year_data['spill_duration'].max()) + 2), alpha=0.3, label=str(year), edgecolor='black', color=colors.get(year))
    ax.set_title(season)
    ax.set_xlabel('Spill Duration')
    ax.set_ylabel('Frequency')
    ax.legend(title='Year')
    ax.grid(True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
'''



#%%

'''

# Calculate total spill hours in each Month for each Year
total_spill_hours_per_month_year = df_spill_hours.groupby(['Year', 'Month']).size().unstack(fill_value=0)

# Create a bar chart of total spill hours in each Month with different colors for each Year
fig, ax = plt.subplots(figsize=(10, 6))

# Plot polygons for each Year with high transparency and add a line for each Year
for year in total_spill_hours_per_month_year.index:
    ax.fill_between(total_spill_hours_per_month_year.columns, 0, total_spill_hours_per_month_year.loc[year], alpha=0.25, label=str(year))
    ax.plot(total_spill_hours_per_month_year.columns, total_spill_hours_per_month_year.loc[year], marker='o')

# Set the x-axis labels to be the Months
ax.set_xticks(total_spill_hours_per_month_year.columns)
ax.set_xticklabels(total_spill_hours_per_month_year.columns)

ax.set_xlabel('Month')
ax.set_ylabel('Total Spill Hours')
ax.set_title('Total Spill Hours in Each Month by Year')
ax.legend(title='Year')
plt.grid(True)
plt.show()


'''
