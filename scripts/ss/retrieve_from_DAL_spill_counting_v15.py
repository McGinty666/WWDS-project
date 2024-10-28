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

site_id = 19505



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

query_formatted_get_signals = query0.format(site_id = site_id)
#query6 = queries['query6']

df_get_signals = processing_functions.execute_query_and_return_df_site_info("sqlTelemetry", query_formatted_get_signals)
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
print('DB_Addr_rising_main_flow:', DB_Addr_rising_main_flow[:1].tolist())
print('Source_rising_main_flow:', Source_rising_main_flow[:1].tolist())

# Remove the first character from each element in the 'DB Addr' Series and join them into a single string
DB_Addr_rising_main_flow_str = ''.join(DB_Addr_rising_main_flow[:1].apply(lambda x: x[1:] if isinstance(x, str) else x))

# Convert the 'Source' Series to a single string
Source_rising_main_flow_str = ''.join(Source_rising_main_flow[:1].apply(lambda x: x if isinstance(x, str) else x)).upper()

print('DB_Addr_rising_main_flow_str:', DB_Addr_rising_main_flow_str)
print('Source_rising_main_flow_str:', Source_rising_main_flow_str)

#%%


#only used for rainfall
easting_value = rounded_x
northing_value = rounded_y


DBAddr_sump = DB_Addr_sump_str
DBAddr_flow_meter = DB_Addr_rising_main_flow_str
SourceSystem_sump = Source_sump_str  
sourcesystem_flow_meter = Source_rising_main_flow_str


#%%


spill_level = 95#5percent of data must be above

#For WestBex use 1670
#For RAFLocking use 95
#Somerford use 90


start_date_spill_query = '2019-01-01'
end_date_spill_query = '2024-10-31'


queries_2 = processing_functions.read_queries('get_spill_hours_query.sql')
query7 = queries_2['query7']

#%%

query_formatted_get_spill_hours = query7.format(start_date_spill_query=start_date_spill_query, end_date_spill_query=end_date_spill_query, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump, spill_level=spill_level)

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
   