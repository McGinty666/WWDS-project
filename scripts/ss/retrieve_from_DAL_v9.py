"""
Created on Tue Oct  1 13:19:28 2024

@author: RMCGINT
"""

import sqlalchemy
import pyodbc
import pandas as pd
import re
from DAL_class_v5 import DAL
import processing_functions
from datetime import datetime


'''
      SITEID          SITENAME                SITETYPE       X       Y
2538   15468  BRADFORD ON TONE  Sewage Pumping Station  316535  121442
Rounded coordinates for SITEID 15468: X=316500, Y=121500
Sump level analogue info for SITEID 15468:
Analogue Server: waste2
Analogue Signal: E7458
Spill(mm): nan
Pre-Spill (mm): nan
Flowmeter signal information for Site Id 15468:
Server: ['WASTE' 'WASTE2']
DB_ADDR: ['E7083' 'E7456']
DB_NAME: ['154680RISING MAIN FLOW' '15468ARISING MAIN FLOW AI']
'''


#only used for rainfall
easting_value = 316500
northing_value = 121500


DBAddr_sump = 7458  
DBAddr_flow_meter = 7456

SourceSystem_sump = 'WASTE2'  #make sure this is capitalized

sourcesystem_flow_meter = 'WASTE2'
'''
# Format the dates to match the ReadingDate format
start_date_str = start_date.strftime('%Y%m%d%H%M')
end_date_str = end_date.strftime('%Y%m%d%H%M')
'''

queries = processing_functions.read_queries('queries_v3.sql')
query1 = queries['query1']
query2 = queries['query2']
query3 = queries['query3']
query4 = queries['query4']
query5 = queries['query5']



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
        

if __name__ == '__main__':
    
    site_id = 15468
    start_date = datetime(2024, 1, 28) #year, month, day
    end_date = datetime(2024, 1, 29) #year, month, day
    
    # Convert dates to string format 'YYYY-MM-DD'
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    
    # Define your queries
    query_formatted_rainfall = query1.format(easting=easting_value, northing=northing_value, start_date=start_date_str, end_date=end_date_str)
    query_formatted_raw_sump = query2.format(start_date=start_date_str, end_date=end_date_str, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
    query_formatted_hour_agg_flow_meter = query3.format(start_date=start_date_str, end_date=end_date_str, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
    query_formatted_daily_agg_sump = query4.format(start_date=start_date_str, end_date=end_date_str, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)
    query_formatted_raw_flow_meter = query5.format(start_date=start_date_str, end_date=end_date_str, DBAddr_flow_meter=DBAddr_flow_meter , sourcesystem_flow_meter=sourcesystem_flow_meter)
    
    
   
# Execute queries and get dataframes
    df_rainfall = processing_functions.execute_query_and_return_df("DALMeteorology", query_formatted_rainfall)
    df_raw_sump = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_raw_sump)
    df_hour_agg_flow_meter = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_hour_agg_flow_meter)
    df_daily_agg_sump = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_daily_agg_sump)
    df_raw_flow_meter = processing_functions.execute_query_and_return_df("sqlTelemetry", query_formatted_raw_flow_meter)


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


if df_daily_agg_sump is not None:
    print("Head of df_daily_agg_sump:")
    print(df_daily_agg_sump.head(5))
    df_daily_agg_sump.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_daily_agg_sump.xlsx', index=False)



if df_raw_flow_meter is not None:
    print("Head of df_raw_flow_meter:")
    print(df_raw_flow_meter.head(5))
    df_raw_flow_meter.to_excel(f'../data/raw/site{site_id}_from_{start_date_str}_to_{end_date_str}_raw_flow_meter.xlsx', index=False)
