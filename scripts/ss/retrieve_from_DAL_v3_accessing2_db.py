"""
Created on Tue Oct  1 13:19:28 2024

@author: RMCGINT
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sqlalchemy
import pyodbc
import pandas as pd
import re


site_id = 19505
start_date = 20200101
end_date = 20220101

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


queries = read_queries('queries.sql')


query2 = queries['query2']




#start of the DAL class

class DAL:
    def __init__(self, db="sqlTelemetry", ODBCDriver=0):
        if not (db == "sqlTelemetry" or db == "DALMeteorology"):
            raise Exception("Invalid database string supplied. Valid databases are sqlTelemetry and DALMeteorology")

        if ODBCDriver == 0:
            drivers = pyodbc.drivers()
            versions = []

            for driver in drivers:
                match = re.search("ODBC Driver.*", driver)
                if match is not None:
                    version = re.search("[0-9]+", driver)
                    versions.append(int(version.group()))

            if len(versions) == 0 or max(versions) < 17:
                raise Exception("No ODBC driver found or old ODBC driver version")

            self.ODBCDriver = max(versions)
        else:
            self.ODBCDriver = ODBCDriver

        self.db = db

    def connect(self):
        connectionRequest = sqlalchemy.engine.URL.create(
            "mssql+pyodbc",
            host="tcp:wx-syn-dal-prd-ondemand.sql.azuresynapse.net,1433",
            database=self.db,
            username="robert.mcginty@wessexwater.co.uk",
            query={
                "driver": f"ODBC Driver {self.ODBCDriver} for SQL Server",
                "TrustServerCertificate": "yes",
                "Connection Timeout": "30",
                "Authentication": "ActiveDirectoryInteractive"
            }
        )

        engine = sqlalchemy.create_engine(connectionRequest)
        self.connection = engine.raw_connection()
        print("Established Connection")

    def query(self, sqlQuery):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sqlQuery)
            except Exception as err:
                cursor.execute(sqlQuery)
            data = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]
            df = pd.DataFrame.from_records(data=data, columns=column_names, index=None)
        return df

    def disconnect(self):
        self.connection.close()
        print("Closed Connection")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

'''
if __name__ == '__main__':
    with DAL("sqlTelemetry", 17) as connection:
        query = query1
'''


if __name__ == '__main__':
    with DAL("DALMeteorology", 17) as connection:
        query = query2

        ret = connection.query(query)
        print(ret)





    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(ret)
    
    output_file_name = 'site'+str(site_id)+'_from_'str(start_date)+'_to_str(end_date)

    # Save the DataFrame to a CSV file
    df.to_csv(f'../data/raw/{output_file_name}.csv', index=False)

    print(f"The query result has been saved to {output_file_name}")