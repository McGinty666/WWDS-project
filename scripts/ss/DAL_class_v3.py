"""
"""

#Replace with your actual email address

import sqlalchemy
import pyodbc
import pandas as pd
import re

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
        self.connection = None
        print(f"Initialized DAL with db: {self.db} and ODBCDriver: {self.ODBCDriver}")

    def connect(self):
        try:
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
        except Exception as e:
            print(f"Failed to establish connection: {e}")
            self.connection = None

    def query(self, sqlQuery):
        if not self.connection:
            raise AssertionError("Database connection is not established.")
        with self.connection.cursor() as cursor:
            cursor.execute(sqlQuery)
            data = cursor.fetchall()
            # Extract only the column names from cursor.description
            column_names = [column for column in cursor.description]
            df = pd.DataFrame.from_records(data=data, columns=column_names, index=None)
        return df



    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()
            print("Closed Connection")
