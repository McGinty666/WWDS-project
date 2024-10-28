"""
Created on Tue Oct  1 13:19:28 2024

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
from tkinter import simpledialog

site_id = 14035

#Somergford is 14035

#%%
from site_information_class import SiteDataProcessor

processor = SiteDataProcessor(
    '../ww_site_info/ww_sites_list.xlsx',
    '../ww_site_info/edm_asset_register.xlsx',
    '../ww_site_info/master_sps_flow_compliance.xlsx'
)

rounded_x, rounded_y = processor.get_rounded_coordinates(site_id)
if rounded_x is not None and rounded_y is not None:
    print(f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}")
else:
    print(f"SITEID {site_id} not found in the data.")


analogue_server, analogue_signal, spill_mm, pre_spill_mm = processor.get_sump_analogue(site_id)
if analogue_server is not None and analogue_signal is not None:
    print(f"Sump level analogue info for SITEID {site_id}:")
    print(f"Analogue Server: {analogue_server}")
    print(f"Analogue Signal: {analogue_signal}")
    print(f"Spill(mm): {spill_mm}")
    print(f"Pre-Spill (mm): {pre_spill_mm}")
else:
    print(f"SITEID {site_id} not found in the asset register data.")


#%%


queries = processing_functions.read_queries('queries_v3.sql')
query0 = queries['query0']
query7 = queries['query7']

#%%

query_formatted_get_signals = query0.format(site_id = site_id)
#query6 = queries['query6']

df_get_signals = processing_functions.execute_query_and_return_df_site_info("sqlTelemetry", query_formatted_get_signals)
print(df_get_signals)



#%%

import tkinter as tk
from tkinter import simpledialog, ttk

# Filter the dataframe to get rows where 'DB Name' contains the string 'sump level'
filtered_df_sump = df_get_signals[df_get_signals['DB Name'].str.contains('sump level', case=False, na=False)]

def get_value():
    selected_value = dropdown_var.get()
    if selected_value == "Custom":
        custom_signal = simpledialog.askstring("Input", "Please enter your custom signal:")
        custom_source = simpledialog.askstring("Input", "Please enter your custom source:")
        if custom_signal and custom_source:
            DB_Addr_sump_var.set(custom_signal)
            Source_sump_var.set(custom_source)
        else:
            print("No custom value entered.")
    else:
        db_name, db_addr = selected_value.split(" - ")
        matching_rows = filtered_df_sump[(filtered_df_sump['DB Name'] == db_name) & (filtered_df_sump['DB Addr'] == db_addr)]
        if not matching_rows.empty:
            selected_row = matching_rows.iloc[0]
            DB_Addr_sump_var.set(selected_row['DB Addr'])
            Source_sump_var.set(selected_row['Source'])
        else:
            print("No matching rows found in the DataFrame.")

    # Create new variables
    DB_Addr_sump_str.set(str(DB_Addr_sump_var.get())[1:])  # Convert to string and remove the first character
    Source_sump_str.set(str(Source_sump_var.get()))  # Convert to string

# Create the main window
root = tk.Tk()
root.title("Select or Enter Sump Level Analog")

# Create a variable to store the dropdown selection
dropdown_var = tk.StringVar(value="Select a value")

# Create a dropdown menu
options = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in filtered_df_sump.iterrows()] + ["Custom"]
dropdown_menu = tk.OptionMenu(root, dropdown_var, *options)
dropdown_menu.pack(pady=10)

# Create a button to confirm the selection
confirm_button = tk.Button(root, text="Confirm", command=get_value)
confirm_button.pack(pady=10)

# Display the dataframe in a treeview
tree = ttk.Treeview(root)
tree["columns"] = list(df_get_signals.columns)
tree["show"] = "headings"
for col in df_get_signals.columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
for index, row in df_get_signals.iterrows():
    tree.insert("", "end", values=list(row))
tree.pack(pady=10)

# Variables to store the selected DB Addr and Source
DB_Addr_sump_var = tk.StringVar()
Source_sump_var = tk.StringVar()

# New variables to store the string conversions
DB_Addr_sump_str = tk.StringVar()
Source_sump_str = tk.StringVar()

# Run the application
root.mainloop()

# Get the final values
db_addr_sump_value = DB_Addr_sump_var.get()
DB_Addr_sump_str.set(str(db_addr_sump_value)[1:])

Source_sump_str.set(str(Source_sump_var.get()))

print('DB_Addr_sump_str:', DB_Addr_sump_str.get())
print('Source_sump_str:', Source_sump_str.get())
print('Type of DB_Addr_sump_str:', type(DB_Addr_sump_str.get()))
print('Type of Source_sump_str:', type(Source_sump_str.get()))



#%%


from tkinter import simpledialog, ttk

# Filter the dataframe to get rows where 'DB Name' contains the string 'rising main flow'
filtered_df_rising_main_flow = df_get_signals[df_get_signals['DB Name'].str.contains('rising main flow', case=False, na=False)]

def get_value():
    selected_value = dropdown_var.get()
    if selected_value == "Custom":
        custom_signal = simpledialog.askstring("Input", "Please enter your custom signal (include the E):")
        custom_source = simpledialog.askstring("Input", "Please enter your custom source :")
        if custom_signal and custom_source:
            print(f"Custom signal entered: {custom_signal}")
            print(f"Custom source entered: {custom_source}")
            DB_Addr_rising_main_flow.set(custom_signal)
            Source_rising_main_flow.set(custom_source)
        else:
            print("No custom value entered.")
    else:
        db_name, db_addr = selected_value.split(" - ")
        matching_rows = filtered_df_rising_main_flow[(filtered_df_rising_main_flow['DB Name'] == db_name) & (filtered_df_rising_main_flow['DB Addr'] == db_addr)]
        if not matching_rows.empty:
            selected_row = matching_rows.iloc[0]
            DB_Addr_rising_main_flow.set(selected_row['DB Addr'])
            Source_rising_main_flow.set(selected_row['Source'])
            print(f"Selected DB Addr: {selected_row['DB Addr']}")
            print(f"Selected Source: {selected_row['Source']}")
        else:
            print("No matching rows found in the DataFrame.")

    # Create new variables
    DB_Addr_rising_main_flow_str.set(DB_Addr_rising_main_flow.get()[1:])  # Convert to string and remove the first character
    Source_rising_main_flow_str.set(str(Source_rising_main_flow.get()))  # Convert to string

# Create the main window
root = tk.Tk()
root.title("Select or Enter Rising Main Flow Analog")

# Create a variable to store the dropdown selection
dropdown_var = tk.StringVar(value="Select a value")

# Create a dropdown menu
options = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in filtered_df_rising_main_flow.iterrows()] + ["Custom"]
dropdown_menu = tk.OptionMenu(root, dropdown_var, *options)
dropdown_menu.pack(pady=10)

# Create a button to confirm the selection
confirm_button = tk.Button(root, text="Confirm", command=get_value)
confirm_button.pack(pady=10)

# Display the dataframe in a treeview
tree = ttk.Treeview(root)
tree["columns"] = list(df_get_signals.columns)
tree["show"] = "headings"
for col in df_get_signals.columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
for index, row in df_get_signals.iterrows():
    tree.insert("", "end", values=list(row))
tree.pack(pady=10)

# Variables to store the selected DB Addr and Source
DB_Addr_rising_main_flow = tk.StringVar()
Source_rising_main_flow = tk.StringVar()

# New variables to store the string conversions
DB_Addr_rising_main_flow_str = tk.StringVar()
Source_rising_main_flow_str = tk.StringVar()

# Run the application
root.mainloop()

# Store the values in new variables
db_addr_rising_main_flow_value = DB_Addr_rising_main_flow.get()
DB_Addr_rising_main_flow_str = db_addr_rising_main_flow_value[1:]

Source_rising_main_flow_str = Source_rising_main_flow.get()

# Print the new variables
print('DB_Addr_rising_main_flow_str:', DB_Addr_rising_main_flow_str)
print('Source_rising_main_flow:', Source_rising_main_flow_str)




#%%


#only used for rainfall
easting_value = rounded_x
northing_value = rounded_y


DB_Addr_sump = DB_Addr_sump_str.get()
DBAddr_flow_meter = DB_Addr_rising_main_flow_str
SourceSystem_sump = Source_sump_var.get()
sourcesystem_flow_meter = Source_rising_main_flow_str


#%%


spill_level = 95#5percent of data must be above

#For WestBex use 1670
#For RAFLocking use 95
#Somerford use 90


start_date_spill_query = '2019-01-01'
end_date_spill_query = '2024-10-27'






#%%

query_formatted_get_spill_hours = query7.format(start_date_spill_query=start_date_spill_query, end_date_spill_query=end_date_spill_query, DBAddr_sump=DB_Addr_sump, SourceSystem_sump=SourceSystem_sump, spill_level=spill_level)

df_spill_hours = processing_functions.execute_query_and_return_df(start_date_spill_query, end_date_spill_query,"sqlTelemetry", query_formatted_get_spill_hours)

if df_spill_hours is not None:
   print("Head of df_spill_hours:")
   print(df_spill_hours.head(5))
   df_spill_hours.to_excel(f'../data/raw/site{site_id}_from_{start_date_spill_query}_to_{end_date_spill_query}_df_spill_hours.xlsx', index=False)





#%%


#EA 12/24 counting

from processing_functions import process_spill_hours

df_spill_hours = processing_functions.process_spill_hours(df_spill_hours)


#%%

from datetime import timedelta
from processing_functions import get_spill_block_periods


df_spill_block_periods = get_spill_block_periods(df_spill_hours)
subset_df_spill_block_periods = df_spill_block_periods.iloc[160:165]
subset_df_spill_block_periods.to_excel(f'../data/raw/site{site_id}_from_{start_date_spill_query}_to_{end_date_spill_query}_spill_block_date_ranges.xlsx')

#%%

'''
# Function to create start_date and end_date
def create_time_periods(df):
    # Create a new dataframe for time periods
    time_periods = pd.DataFrame()
    
    # Combine Year, Month, Day into a single datetime column
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    
    # Calculate start_date and end_date
    time_periods['start_date'] = df['Date'] - timedelta(days=1)
    time_periods['end_date'] = df['Date'] + timedelta(days=1)
    
    return time_periods

# Create the new dataframe with start_date and end_date
time_periods_screened = create_time_periods(df_daily_agg_sump_screened)

print(time_periods_screened)

'''


#%%

queries = processing_functions.read_queries('queries_v3.sql')
query1 = queries['query1']
query2 = queries['query2']
query3 = queries['query3']
query4 = queries['query4']
query5 = queries['query5']


        
'''
date_ranges_df = pd.DataFrame({
    'start_date': ['2024-09-20', '2024-03-10'],
    'end_date': ['2024-09-25', '2024-03-27']
})
'''

date_ranges_df = subset_df_spill_block_periods 

date_ranges_df.head(5)


#%%  
   
# Execute queries and get dataframes
for index, row in date_ranges_df.iterrows():
    start_date = row['start_date']
    end_date = row['end_date']
    #start_date_str = start_date.strftime('%Y-%m-%d')
    #end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date
    end_date_str = end_date
    # Define your queries
    query_formatted_rainfall = query1.format(easting=easting_value, northing=northing_value, start_date=start_date, end_date=end_date)
    query_formatted_raw_sump = query2.format(start_date=start_date, end_date=end_date, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
    query_formatted_hour_agg_flow_meter = query3.format(start_date=start_date, end_date=end_date, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
    #   query_formatted_daily_agg_sump = query4.format(start_date=start_date, end_date=end_date, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
    query_formatted_raw_flow_meter = query5.format(start_date=start_date, end_date=end_date, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
        


    df_rainfall = processing_functions.execute_query_and_return_df(start_date, end_date,"DALMeteorology", query_formatted_rainfall)
    df_raw_sump = processing_functions.execute_query_and_return_df(start_date, end_date,"sqlTelemetry", query_formatted_raw_sump)
    df_hour_agg_flow_meter = processing_functions.execute_query_and_return_df(start_date, end_date,"sqlTelemetry", query_formatted_hour_agg_flow_meter)
    #   df_daily_agg_sump = processing_functions.execute_query_and_return_df(start_date, end_date,"sqlTelemetry", query_formatted_daily_agg_sump)
    df_raw_flow_meter = processing_functions.execute_query_and_return_df(start_date, end_date,"sqlTelemetry", query_formatted_raw_flow_meter)
    
    
    # Print the head(5) of each DataFrame and save to Excel
    if df_rainfall is not None:
        print("Head of df_rainfall:")
        print(df_rainfall.head(5))
        df_rainfall.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_rainfall.xlsx', index=False)
    
    if df_raw_sump is not None:
        print("Head of df_raw_sump:")
        print(df_raw_sump.head(5))
        df_raw_sump.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_sump.xlsx', index=False)
    
    if df_hour_agg_flow_meter is not None:
        print("Head of df_hour_agg_flow_meter:")
        print(df_hour_agg_flow_meter.head(5))
        df_hour_agg_flow_meter.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_hour_agg_flow_meter.xlsx', index=False)
    
    '''
    if df_daily_agg_sump is not None:
        print("Head of df_daily_agg_sump:")
        print(df_daily_agg_sump.head(5))
        df_daily_agg_sump.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_daily_agg_sump.xlsx', index=False)
    '''
    if df_raw_flow_meter is not None:
        print("Head of df_raw_flow_meter:")
        print(df_raw_flow_meter.head(5))
        df_raw_flow_meter.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_flow_meter.xlsx', index=False)



#%%



# Group by year and calculate the required counts and sums
grouped = df_spill_hours.groupby('Year').agg(
    EA_12_24_count=('EA_12_24_counter', 'nunique'),
    spill_event_count=('spill_event_id', 'nunique')
).reset_index()

# Merge with df_spill_hours to get spill hours total
result = pd.merge(grouped, df_spill_hours, on='Year')

# Calculate the ratio column
result['EA_12_24 / spill_event_id_count'] = result['EA_12_24_count'] / result['spill_event_count']

# Select only the newly created columns
new_df = result[['Year', 'EA_12_24_count', 'spill_event_count', 'EA_12_24 / spill_event_id_count']]

print(new_df)




#%%
'''
given a dataframe with columns spill_event_duration and spill_event_id, create a box-plot which has the distribution of spill_event_durations for a given unique spill_event_id
'''

# Convert spill_hours to datetime
df_spill_hours['spill_hours'] = pd.to_datetime(df_spill_hours['spill_hours'])

# Extract year from spill_hours
df_spill_hours['year'] = df_spill_hours['spill_hours'].dt.year

# Group by year and spill_event_id and get the maximum spill_event_duration for each group
max_durations = df_spill_hours.groupby(['year', 'spill_event_id'])['spill_event_duration'].max().reset_index()

# Create a box plot for the distribution of the maximum spill_event_durations for each year
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
sns.boxplot(x='year', y='spill_event_duration', data=max_durations)
plt.title('Distribution of Spill Event Durations by Year')
plt.xlabel('Year')
plt.ylabel('Maximum Spill Event Duration (hours)')



# Create an overall box plot for the distribution of the maximum spill_event_durations
plt.subplot(1, 2, 2)
sns.boxplot(y=max_durations['spill_event_duration'])
plt.title('Overall Distribution of Spill Event Durations')
plt.ylabel('Maximum Spill Event Duration (hours)')



plt.gca().set_aspect(0.075)

plt.tight_layout()
plt.show()

###
#%%

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


#%%


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
ax.set_title(f'Total Spill Hours in Each Month by Year for Site ID {site_id} using sump level {DB_Addr_sump_str}')
ax.legend(title='Year')
plt.grid(True)
plt.show()



