import sqlalchemy
import pyodbc
import pandas as pd

def dalConnect(db = "sqlTelemetry", ODBCDriver = 18):
	# Standard function for connection to the DAL. Uses active directory interface to connect, which requires you to enter your
	# WW email and password. Returns an sqlalchemy raw_connection object holding the connection to the DAL. Default conncetion 
	# to sqlTelemetry. Optionsare are sqlTelemetry and DALMeteorology
	
	if not (db == "sqlTelemetry" or db == "DALMeteorology"):
		raise Exception("Invalid database string supplied. Valid databases are sqlTelemetry and DALMeteorology")

	connectionRequest = sqlalchemy.engine.URL.create(
		"mssql+pyodbc",
		host = "tcp:wx-syn-dal-prd-ondemand.sql.azuresynapse.net,1433",
		database = db,
		username = "@wessexwater.co.uk",
		query = {
			"driver": f"ODBC Driver {ODBCDriver} for SQL Server",
			"TrustServerCertificate": "yes",
			"Connection Timeout": "30",
			"Authentication": "ActiveDirectoryInteractive"
		}
	)

	engine = sqlalchemy.create_engine(connectionRequest)
	establishedConnection = engine.raw_connection()
	print("Established Connection")

	return establishedConnection

def query(sqlQuery, connection):
	# Function to make querying the dal easier. Takes sqlQuery as a string of the sql query you wish to make, and connection as
	# a sqlalchemy raw_connection, as generated above. Function is designed to avoid error case where DAL occasionally returns
	# nothing. Returns a pandas dataframe holding the results of the query.

	with connection.cursor() as cursor:
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


if __name__ == '__main__':
	# Example code
	
	connection = dalConnect("DALMeteorology", 18)

	ret = query("SELECT * FROM WDC.NimrodReadings WHERE Year = 2023 AND Month = 01 AND Day = 01", connection)

	print(ret)

	connection.close()