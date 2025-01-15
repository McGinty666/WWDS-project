import sqlalchemy
import pyodbc
import pandas as pd
import re
import sys
import os
import pathlib
from DAL_Class import DAL
import time

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
	# connection = dalConnect()

	# Query DAL and add results to data frames
	with DAL() as connection:
		siteWasteESignals = connection.query(wasteESearch)
		siteWasteBSignals = connection.query(wasteBSearch)
		siteWaste2ESignals = connection.query(waste2ESearch)
		siteWaste2BSignals = connection.query(waste2BSearch)

	# Close connection
	# connection.close()
	# print("Closed Connection")

	# Compose all signals to a single dataframe and sort by site ID for easier processing
	allSignalsList = [siteWaste2BSignals, siteWaste2ESignals, siteWasteBSignals, siteWasteESignals]
	allSignals = pd.concat(allSignalsList)
	allSignals["Site ID"] = allSignals["DB Name"].str[:5].apply(pd.to_numeric)
	allSignals.sort_values("Site ID", inplace=True)

	# Write signals out to csv for anaysis by user.
	print("Writing Out")
	allSignals.to_csv(r".\Signallist.csv")
	print(fr"Done. Signals available at {os.getcwd()}\Signallist.csv")

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

	# Get year range from user input and clean
	year_range = input(r"Please enter start and end year (inclusive) as a comma separated list. For a single year enter start year equal to end year: ")
	clean_year_range = re.sub("\s+", "", year_range).casefold()

	# Turn input string into start and end year, then loop over range to get every year and add to string to add to query
	try:
		start_year, end_year = clean_year_range.split(",")
	except Exception as err:
		print("Too many years entered for year range")
		print(err)
	year_string = ""
	for year in range(int(start_year), int(end_year) + 1):
		if year_string == "":
			year_string += "'" + str(year) + "'"
		else:
			year_string += ", '" + str(year) + "'"

	# Adding column to query against DAL as B/E signals are distinguished by table. Has error handling if non-numeric
	# signal ID found.
	try:
		signals["Signal Numeric"] = signals["DB Addr"].str[1:].apply(pd.to_numeric)
	except Exception as err:
		print("Non-numeric signal id found. Please check csv")
		print(err)

	sep = ", "
	query_signals = {}
	for server in ["Waste", "Waste2"]:
		for sig_type in ["B", "E"]:
			# One liner filters signals by B/E and source system, culls to final column, converts to list, then converts list to comma separated string 
			# and wraps in brackets to add to query, then adds to dictionary
			query_signals[server + sig_type] = "(" + sep.join(str(x) for x in list(signals.loc[(signals["DB Addr"].str[0] == sig_type) & (signals["Source"] == server)]["Signal Numeric"])) + ")"

	# Connect to DAL
	# connection = dalConnect()

	# Query DAL with the various lists, checking to ensure that lists are empty so as to avoid uneccessary queries.
	data_dict = {}
	with DAL() as connection:
		for key in query_signals:
			if not query_signals[key] == "()":
				if key[-1] == "E":
					view = "AnaloguesView"
				else:
					view = "DigitalsView"
				search = f"""SELECT SourceSystem, DbAddr, Time, {key[-1]}Value FROM {view} WHERE DbAddr IN {query_signals[key]} AND SourceSystem = '{key[:-1].upper()}' AND Year IN ({year_string})"""
				print("Querying: " + search)
				t = time.process_time()
				data_dict[key] = connection.query(search)
				t = time.process_time() - t
				print("Time Elapsed: " + str(t))

	# Close connection
	# connection.close()
	# print("Closed Connection")

	# Split out signals to dataframes with naming convention as per standard signal downloads. Each dataframe holds mutliple signals, so
	# the frames are filtered on signal numeric to acquire single signals. Signals are also sorted by time, as they are returned from 
	# the DAL in access order, which is fairly random
	pathlib.Path("./download").mkdir(exist_ok=True)
	signal_dict = {}
	for key in data_dict:
		print(f"Writing {key[:-1]} {key[-1]} signals to dict")
		try:
			for signal in list(signals.loc[(signals["DB Addr"].str[0] == key[-1]) & (signals["Source"] == key[:-1])]["Signal Numeric"]):
				signal_dict[f"{key[:-1].upper()}_{key[-1]}{signal}"] = data_dict[key].loc[data_dict[key]["DbAddr"] == signal].sort_values("Time") # .to_csv(f"./download/{key[:-1].upper()}_{key[-1]}{signal}.csv", header = False, index = False)
		except Exception as err:
			print(f"No {key} signals to export or")
			print(err)

	for key in signal_dict:
		print(f"Writing {key} signal to file")
		signal_dict[key].drop(labels = "SourceSystem", axis = 1).to_csv(f"./download/{key}.csv", header = False, index = False)

else:
	raise Exception("Allowed responses are download or listing.")