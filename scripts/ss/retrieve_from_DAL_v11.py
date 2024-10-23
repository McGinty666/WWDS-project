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

site_id = 14035

queries = processing_functions.read_queries('queries_v3.sql')
query0 = queries['query0']

query_formatted_get_signals = query0.format(site_id = site_id)
#query6 = queries['query6']

df_get_signals = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_get_signals)
print(df_get_signals)

#%%


# Filter the dataframe to get rows where 'DB Name' contains the string 'sump level'
filtered_df_sump = df_get_signals[df_get_signals['DB Name'].str.contains('sump level', case=False, na=False)]

# Report the value of 'DB Addr' and 'Source'
DB_Addr_sump = filtered_df_sump['DB Addr']
Source_sump = filtered_df_sump['Source']


#%%




# Convert Series to list and print each value
print('DB_Addr_sump:', DB_Addr_sump[:1].tolist())
print('Source_sump:', Source_sump[:1].tolist())

# Remove the first character from each element in the Series and join them into a single string
DB_Addr_sump_str = ''.join(DB_Addr_sump[:1].apply(lambda x: x[1:] if isinstance(x, str) else x))

# Convert the 'Source' Series to a single string
Source_sump_str = ''.join(Source_sump[:1].apply(lambda x: x if isinstance(x, str) else x)).upper()


#%%%
'''

#Use this code if you have 2 sump addresses and you want to use the second

# Convert Series to list and print each value
print('DB_Addr_sump:', DB_Addr_sump[1:].tolist())
print('Source_sump:', Source_sump[1:].tolist())

# Remove the first character from each element in the Series and join them into a single string
DB_Addr_sump_str = ''.join(DB_Addr_sump[1:].apply(lambda x: x[1:] if isinstance(x, str) else x))

# Convert the 'Source' Series to a single string
Source_sump_str = ''.join(Source_sump[1:].apply(lambda x: x if isinstance(x, str) else x)).upper()

'''
#%%
print('DB_Addr_sump_str:', DB_Addr_sump_str)
print('Source_sump_str:', Source_sump_str)

#%%

# Filter the dataframe to get rows where 'DB Name' contains the string 'rising main flow'
filtered_df_rising_main_flow = df_get_signals[df_get_signals['DB Name'].str.contains('rising main flow', case=False, na=False)]

# Report the value of 'DB Addr' and 'Source'
DB_Addr_rising_main_flow = filtered_df_rising_main_flow['DB Addr']
Source_rising_main_flow = filtered_df_rising_main_flow['Source']

# Convert Series to list and print each value
print('DB_Addr_rising_main_flow:', DB_Addr_rising_main_flow.tolist())
print('Source_rising_main_flow:', Source_rising_main_flow.tolist())

# Remove the first character from each element in the 'DB Addr' Series and join them into a single string
DB_Addr_rising_main_flow_str = ''.join(DB_Addr_rising_main_flow.apply(lambda x: x[1:] if isinstance(x, str) else x))

# Convert the 'Source' Series to a single string
Source_rising_main_flow_str = ''.join(Source_rising_main_flow.apply(lambda x: x if isinstance(x, str) else x)).upper()

print('DB_Addr_rising_main_flow_str:', DB_Addr_rising_main_flow_str)
print('Source_rising_main_flow_str:', Source_rising_main_flow_str)

#%%
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

#%%


#only used for rainfall
easting_value = rounded_x
northing_value = rounded_y


DBAddr_sump = DB_Addr_sump_str
DBAddr_flow_meter = DB_Addr_rising_main_flow_str
SourceSystem_sump = Source_sump_str  
sourcesystem_flow_meter = Source_rising_main_flow_str


#%%


queries = processing_functions.read_queries('queries_v3.sql')
query1 = queries['query1']
query2 = queries['query2']
query3 = queries['query3']
query4 = queries['query4']
query5 = queries['query5']


        

start_date = datetime(2023, 1, 3) #year, month, day
end_date = datetime(2023, 1, 5) #year, month, day

# Convert dates to string format 'YYYY-MM-DD'
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')


# Define your queries
query_formatted_rainfall = query1.format(easting=easting_value, northing=northing_value, start_date=start_date_str, end_date=end_date_str)
query_formatted_raw_sump = query2.format(start_date=start_date_str, end_date=end_date_str, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
query_formatted_hour_agg_flow_meter = query3.format(start_date=start_date_str, end_date=end_date_str, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
#   query_formatted_daily_agg_sump = query4.format(start_date=start_date_str, end_date=end_date_str, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
#    query_formatted_raw_flow_meter = query5.format(start_date=start_date_str, end_date=end_date_str, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
    
    
   
# Execute queries and get dataframes
df_rainfall = processing_functions.execute_query_and_return_df("DALMeteorology", query_formatted_rainfall)
df_raw_sump = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_raw_sump)
df_hour_agg_flow_meter = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_hour_agg_flow_meter)
#   df_daily_agg_sump = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_daily_agg_sump)
#   df_raw_flow_meter = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_raw_flow_meter)


# Print the head(5) of each dataframe and save to xlsx
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



if df_raw_flow_meter is not None:
    print("Head of df_raw_flow_meter:")
    print(df_raw_flow_meter.head(5))
    df_raw_flow_meter.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_flow_meter.xlsx', index=False)
'''