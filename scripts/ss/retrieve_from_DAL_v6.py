"""
Created on Tue Oct  1 13:19:28 2024

@author: RMCGINT
"""

import sqlalchemy
import pyodbc
import pandas as pd
import re
from DAL_class_v2 import DAL
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



site_id = 15468


#only used for rainfall
easting_value = 316500
northing_value = 121500

start_date = datetime(2024, 1, 1) #year, month, day
end_date = datetime(2024, 1, 2) #year, month, day



# Convert dates to string format 'YYYY-MM-DD'
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')



DBAddr_sump = 7458  
DBAddr_flow_meter = 7456

SourceSystem_sump = 'WASTE2'  #make sure this is capitalized

sourcesystem_flow_meter = 'WASTE2'
'''
# Format the dates to match the ReadingDate format
start_date_str = start_date.strftime('%Y%m%d%H%M')
end_date_str = end_date.strftime('%Y%m%d%H%M')
'''

queries = processing_functions.read_queries('queries_v2.sql')
#query2 = queries['query2']
query4 = queries['query4']
query5 = queries['query5']


#query_formatted_rainfall = query2.format(easting=easting_value, northing=northing_value, start_date=start_date_str, end_date=end_date_str)
#query_formatted_raw_sump = query4.format(start_date=start_date_str, end_date=end_date_str, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump)

query_formatted_raw_flow_meter = query5.format(start_date=start_date_str, end_date=end_date_str, DBAddr_flow_meter=DBAddr_flow_meter, sourcesystem_flow_meter=sourcesystem_flow_meter)

'''
if __name__ == '__main__':
    with DAL("sqlTelemetry", 17) as connection:
        if connection.connection is None:
            print("Failed to establish connection")
        else:
            query = query_formatted_raw_sump
            ret = connection.query(query)
            print(ret)
'''            
    
if __name__ == '__main__':
    with DAL("sqlTelemetry", 17) as connection:
        if connection.connection is None:
            print("Failed to establish connection")
        else:
            query = query_formatted_raw_flow_meter
            ret = connection.query(query)
            print(ret)


'''
if __name__ == '__main__':
    with DAL("DALMeteorology", 17) as connection:
        if connection.connection is None:
            print("Failed to establish connection")
        else:
            query = query_formatted_rainfall
            ret = connection.query(query)
            print(ret)
'''
    # Convert the result to a pandas DataFrame
df = pd.DataFrame(ret)

output_file_name = f'site{site_id}_from_{start_date_str}_to_{end_date_str}'

# Save the DataFrame to a CSV file
df.to_csv(f'../data/raw/{output_file_name}.csv', index=False)

print(f"The query result has been saved to {output_file_name}")
