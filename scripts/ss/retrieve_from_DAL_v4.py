R"""
Created on Tue Oct  1 13:19:28 2024

@author: RMCGINT
"""

import sqlalchemy
import pyodbc
import pandas as pd
import re
from DAL_class_v2 import DAL
import processing_functions


site_id = 19505
start_date = 'start'
end_date = 'end'

easting_value = 336500
northing_value = 160500


queries = processing_functions.read_queries('queries.sql')
query2 = queries['query2']
query_formatted = query2.format(easting=easting_value, northing=northing_value)



#query2 = queries['query2']
#query1 = queries['query1']

'''
if __name__ == '__main__':
    with DAL("sqlTelemetry", 17) as connection:
        if connection.connection is None:
            print("Failed to establish connection")
        else:
            query = query_formatted
            ret = connection.query(query)
            print(ret)
'''

if __name__ == '__main__':
    with DAL("DALMeteorology", 17) as connection:
        if connection.connection is None:
            print("Failed to establish connection")
        else:
            query = query_formatted
            ret = connection.query(query)
            print(ret)

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(ret)

    output_file_name = f'site{site_id}_from_{start_date}_to_{end_date}'

    # Save the DataFrame to a CSV file
    df.to_csv(f'../data/raw/{output_file_name}.csv', index=False)

    print(f"The query result has been saved to {output_file_name}")
