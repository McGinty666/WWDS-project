import sqlalchemy
import pyodbc
import pandas as pd
import re

class DAL:
	def __init__(self, db = "sqlTelemetry", ODBCDriver = 0):
	# Initializaton function of the class. Will default to telemetry database, and uses autodetection to find the most up to 
	# date ODBC driver version it can use. Can be manually supplied with an ODBC driver version to override autodetect 
	# behavior. Driver version must be greater than 17 for connect method to function correctly. Currently only two databases
	# available to connect to, so validates against them.

		if not (db == "sqlTelemetry" or db == "DALMeteorology"):
			raise Exception("Invalid database string supplied. Valid databases are sqlTelemetry and DALMeteorology")

		if ODBCDriver == 0:
			drivers = pyodbc.drivers()
			versions = []

			for driver in drivers:
				match = re.search("ODBC Driver.*", driver)
				if match != None:
					version = re.search("[0-9]+", driver)
					versions.append(int(version.group()))

			if len(versions) == 0 or max(versions) < 17:
				raise Exception("No ODBC driver found or old ODBC driver version")

			self.ODBCDriver = max(versions)
		else:
			self.ODBCDriver = ODBCDriver

		self.db = db

	def connect(self):
	# Standard function for connection to the DAL. Uses active directory interface to connect, which requires you to enter your
	# WW email and password. Returns an sqlalchemy raw_connection object holding the connection to the DAL. Connects to DAL using
	# variables defined on initialization (self.db and self.ODBCDriver)

		connectionRequest = sqlalchemy.engine.URL.create(
			"mssql+pyodbc",
			host = "tcp:wx-syn-dal-prd-ondemand.sql.azuresynapse.net,1433",
			database = self.db,
			username = "@wessexwater.co.uk",
			query = {
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
	# Function to make querying the dal easier. Takes sqlQuery as a string of the sql query you wish to make, and connection as
	# a sqlalchemy raw_connection, as generated above. Function is designed to avoid error case where DAL occasionally returns
	# nothing. Returns a pandas dataframe holding the results of the query.

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(sqlQuery)
			except Exception as err:
				cursor.execute(sqlQuery)
			if cursor.messages:
				data = cursor.fetchall()
				column_names = [column[0] for column in cursor.description]
				df = pd.DataFrame.from_records(data=data, columns=column_names, index=None)
			else:
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

if __name__ == '__main__':
	# Example code

	# from DAL_Class import DAL

	with DAL("sqlTelemetry", 18) as connection:
		ret = connection.query("SELECT Source, [DB Addr], [DB Name], Text1, [OS Name] FROM DALReport.TelexWasteAnalogues WHERE [DB Name] LIKE '15551%'")

	print(ret)