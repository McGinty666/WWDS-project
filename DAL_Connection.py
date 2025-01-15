import sqlalchemy
import pyodbc
import pandas as pd
import re
import sys
import pathlib
import time

def dalConnect():
	# Standard function for connection to the DAL. Uses active directory interface to connect, which requires you to enter your
	# WW email and password. Returns an sqlalchemy raw_connection object holding the connection to the DAL.
	
	connectionRequest = sqlalchemy.engine.URL.create(
		"mssql+pyodbc",
		host = "tcp:wx-syn-dal-prd-ondemand.sql.azuresynapse.net,1433",
		database = "sqlTelemetry",
		username = "@wessexwater.co.uk",
		query = {
			"driver": "ODBC Driver 18 for SQL Server",
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

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Main process starts here

# Get user input to decide which mode we are in. Cleans input so some variation is allowed. Modes are signal listing, for finding
# signals associated with a site, and data download, for getting data associated with found signals.
mode = input("Do you require a signal listing or a data download [download/listing]? ")
cleanMode = re.sub("\s+", "", mode).casefold()

if cleanMode == "listing":

	# Get user input for sites required. Multiline input so that peole can copy and paste from excel. Turns this input
	# into a list of site IDs
	print("Please enter site IDs you require signal data for as a comma separated list or copy and paste from Excel. Press Ctrl-Z then Enter on a new line to end input: ", end='', file=sys.stderr, flush=True)
	sites = sys.stdin.readlines()
	siteArr = []
	for item in sites:
		IDarr = re.sub("\s+", "", item).split(",")
		for ID in IDarr:
			if not id == "":
				siteArr.append(ID)

	# String builder to build the clauses for the sql query we are going to pass to the DAL. Checks that site ID is 
	# numeric to avoid sql injection attempts.
	clauses = ""
	for ID in siteArr:
		if not ID.isnumeric():
			raise Exception(f"Site ID must be an integer. Failed ID: {ID}")

		if clauses == "":
			clauses = clauses + f"[DB Name] LIKE '{ID}%'"
		else:
			clauses = clauses + f" OR [DB Name] LIKE '{ID}%'"

	# Build the various queries which we want to hit the DAL with. We need to query 4 different tables to capture all
	# relevant signals
	wasteESearch = """SELECT Source, [DB Addr], [DB Name], Text1, [OS Name] FROM DALReport.TelexWasteAnalogues WHERE """ + clauses
	wasteBSearch = """SELECT Source, [DB Addr], [DB Name], Text1, [OS Name] FROM DALReport.TelexWasteBooleans WHERE """ + clauses
	waste2ESearch = """SELECT Source, [DB Addr], [DB Name], Text1, [OS Name] FROM DALReport.TelexWaste2Analogues WHERE """ + clauses
	waste2BSearch = """SELECT Source, [DB Addr], [DB Name], Text1, [OS Name] FROM DALReport.TelexWaste2Booleans WHERE """ + clauses

	# Connect to DAL
	connection = dalConnect()

	# Query DAL and add results to data frames
	siteWasteESignals = query(wasteESearch, connection)
	siteWasteBSignals = query(wasteBSearch, connection)
	siteWaste2ESignals = query(waste2ESearch, connection)
	siteWaste2BSignals = query(waste2BSearch, connection)

	# Close connection
	connection.close()
	print("Closed Connection")

	# Compose all signals to a single dataframe and sort by site ID for easier processing
	allSignalsList = [siteWaste2BSignals, siteWaste2ESignals, siteWasteBSignals, siteWasteESignals]
	allSignals = pd.concat(allSignalsList)
	allSignals["Site ID"] = allSignals["DB Name"].str[:5].apply(pd.to_numeric)
	allSignals.sort_values("Site ID", inplace=True)

	# Write signals out to csv for anaysis by user.
	allSignals.to_csv(r".\Signallist.csv")

elif cleanMode == "download":

	# Get user input for filepath to csv containing signals to download. Some sanitization.
	source = input(r"Use default source (.\Signallist.csv) or custom filepath. Expected columns are Source, [DB Addr], [DB Name], Text1, [OS Name], [Site ID] with index column as column 0. [default/'filepath']? ")
	cleanSource = re.sub("\s+", "", source).casefold()

	# Checks for existence of file and raises error if not.
	path = pathlib.Path(source)
	if cleanSource == "default":
		path = pathlib.Path(r".\Signallist.csv")
		if not path.is_file():
			raise Exception("Could not find file. Please verify that file exists.")
		csvLocation = r".\Signallist.csv"
	elif path.is_file():
		csvLocation = source
	else:
		raise Exception("Could not find file. Please verify that file exists and that path is spelt correctly.")

	# Read in signals to pandas dataframe
	signals = pd.read_csv(csvLocation, index_col=0)

	# Adding column to query against DAL as B/E signals are distinguished by table. Has error handling if non-numeric
	# signal ID found.
	try:
		signals["Signal Numeric"] = signals["DB Addr"].str[1:].apply(pd.to_numeric)
	except Exception as err:
		raise Exception("Non-numeric signal id found. Please check csv" + err)

	# One liner filters signals by B/E and source system, culls to final column, converts to list, then converts list to comma separated string 
	# and wraps in brackerts to add to query
	sep = ", "
	wasteBSignals = "(" + sep.join(str(x) for x in list(signals.loc[(signals["DB Addr"].str[0] == "B") & (signals["Source"] == "Waste")]["Signal Numeric"])) + ")"
	wasteESignals = "(" + sep.join(str(x) for x in list(signals.loc[(signals["DB Addr"].str[0] == "E") & (signals["Source"] == "Waste")]["Signal Numeric"])) + ")"
	waste2BSignals = "(" + sep.join(str(x) for x in list(signals.loc[(signals["DB Addr"].str[0] == "B") & (signals["Source"] == "Waste2")]["Signal Numeric"])) + ")"
	waste2ESignals = "(" + sep.join(str(x) for x in list(signals.loc[(signals["DB Addr"].str[0] == "E") & (signals["Source"] == "Waste2")]["Signal Numeric"])) + ")"

	# Connect to DAL
	connection = dalConnect()

	# Could simplify a lot of this with a loop, but 4 times isn't too bad. Query DAL with the various lists, checking to ensure that lists
	# are empty so as to avoid uneccessary queries.
	if not wasteESignals == "()":
		search = f"""SELECT Time, TimeGMT, DbAddr, SourceSystem, EValue FROM AnaloguesView WHERE DbAddr IN {wasteESignals} AND SourceSystem = 'WASTE' AND Year IN ('2017', '2018', '2019', '2020', '2021', '2022', '2023')"""
		print("Querying: " + search)
		t = time.process_time()
		wasteEData = query(search, connection)
		t = time.process_time() - t
		print("Time Elapsed: " + str(t))

	if not waste2ESignals == "()":
		search = f"""SELECT Time, TimeGMT, DbAddr, SourceSystem, EValue FROM AnaloguesView WHERE DbAddr IN {waste2ESignals} AND SourceSystem = 'WASTE2' AND Year IN ('2017', '2018', '2019', '2020', '2021', '2022', '2023')"""
		print("Querying: " + search)
		t = time.process_time()
		waste2EData = query(search, connection)
		t = time.process_time() - t
		print("Time Elapsed: " + str(t))

	if not wasteBSignals == "()":
		search = f"""SELECT Time, TimeGMT, DbAddr, SourceSystem, BValue FROM DigitalsView WHERE DbAddr IN {wasteBSignals} AND SourceSystem = 'WASTE' AND Year IN ('2017', '2018', '2019', '2020', '2021', '2022', '2023')"""
		print("Querying: " + search)
		t = time.process_time()
		wasteBData = query(search, connection)
		t = time.process_time() - t
		print("Time Elapsed: " + str(t))

	if not waste2BSignals == "()":
		search = f"""SELECT Time, TimeGMT, DbAddr, SourceSystem, BValue FROM DigitalsView WHERE DbAddr IN {waste2BSignals} AND SourceSystem = 'WASTE2' AND Year IN ('2017', '2018', '2019', '2020', '2021', '2022', '2023')"""
		print("Querying: " + search)
		t = time.process_time()
		waste2BData = query(search, connection)
		t = time.process_time() - t
		print("Time Elapsed: " + str(t))

	# Close connection
	connection.close()
	print("Closed Connection")

	# Write out signals to csvs with naming convention as per standard signal downloads. Each dataframe holds mutliple signals, so
	# the frames are filtered on signal numeric to acquire single signals. Signals are also sorted by time, as they are returned from 
	# the DAL in access order, which is fairly random
	try:
		for signal in list(signals.loc[(signals["DB Addr"].str[0] == "B") & (signals["Source"] == "Waste")]["Signal Numeric"]):
			wasteBData.loc[wasteBData["DbAddr"] == signal].sort_values("Time").to_csv(f"./WASTE_B{signal}.csv")
	except Exception as err:
		print("No Waste B signals to export" + err)

	try:
		for signal in list(signals.loc[(signals["DB Addr"].str[0] == "B") & (signals["Source"] == "Waste2")]["Signal Numeric"]):
			wasteB2Data.loc[waste2BData["DbAddr"] == signal].sort_values("Time").to_csv(f"./WASTE2_B{signal}.csv")
	except Exception as err:
		print("No Waste2 B signals to export" + err)

	try:
		for signal in list(signals.loc[(signals["DB Addr"].str[0] == "E") & (signals["Source"] == "Waste")]["Signal Numeric"]):
			wasteEData.loc[wasteEData["DbAddr"] == signal].sort_values("Time").to_csv(f"./WASTE_E{signal}.csv")
	except Exception as err:
		print("No Waste E signals to export" + err)

	try:
		for signal in list(signals.loc[(signals["DB Addr"].str[0] == "E") & (signals["Source"] == "Waste2")]["Signal Numeric"]):
			wasteE2Data.loc[waste2EData["DbAddr"] == signal].sort_values("Time").to_csv(f"./WASTE2_E{signal}.csv")
	except Exception as err:
		print("No Waste2 E signals to export" + err)

else:
	raise Exception("Allowed responses are download or listing.")