# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 19:25:15 2024

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
import tkinter as tk
from tkinter import simpledialog, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import math

class SiteInformationApp:
    def __init__(self, root):
        self.filtered_df_rising_main_flow = None
        self.filtered_df_sump = None
        self.root = root
        self.root.title("Site Information")
        self.root.configure(bg='light blue')

        self.setup_ui()
        self.df_spill_hours = None
        self.site_id = None  # Initialize the instance variable
        self.default_spill_level = 95

    def setup_ui(self):
        tk.Label(self.root, text="Enter Site ID:", bg='light blue').pack(pady=5)
        self.entry_site_id = tk.Entry(self.root)
        self.entry_site_id.pack(pady=5)

        self.btn_get_signals = tk.Button(self.root, text="Get Signals", command=self.get_signals)
        self.btn_get_signals.pack(pady=5)

        self.output_text_1 = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.output_text_1.pack(pady=5)
        self.output_text_1.configure(bg="light blue")

        frame = tk.Frame(self.root, bg='light blue')
        frame.pack(pady=5)

        self.tree = ttk.Treeview(frame)
        self.tree.pack(side="left")

        scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        scrollbar.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar.set)

        right_frame = tk.Frame(self.root, bg='light blue')
        right_frame.pack(side="right", padx=10, pady=10, anchor='ne')

        self.dropdown_var_sump = tk.StringVar(value="Select level analog signal")
        self.dropdown_menu_sump = tk.OptionMenu(right_frame, self.dropdown_var_sump, "Select level analog signal (dropdown)")
        self.dropdown_menu_sump.pack(side="left", pady=5)

        self.confirm_button_sump = tk.Button(right_frame, text="Confirm selected level analog", command=self.get_value_sump)
        self.confirm_button_sump.pack(side="right", pady=5)

        self.dropdown_var = tk.StringVar(value="Select flow meter signal")
        self.dropdown_menu = tk.OptionMenu(right_frame, self.dropdown_var, "Select flow meter signal (dropdown)")
        self.dropdown_menu.pack(side="left", pady=5)

        self.confirm_button = tk.Button(right_frame, text="Confirm flow meter signal", command=self.get_value)
        self.confirm_button.pack(side="right", pady=5)

        self.DB_Addr_rising_main_flow = tk.StringVar()
        self.Source_rising_main_flow = tk.StringVar()
        self.DB_Addr_rising_main_flow_str = tk.StringVar()
        self.Source_rising_main_flow_str = tk.StringVar()
        self.DB_Addr_sump_var = tk.StringVar()
        self.Source_sump_var = tk.StringVar()
        self.DB_Addr_sump_str = tk.StringVar()
        self.Source_sump_str = tk.StringVar()

        self.btn_run_spill_query = tk.Button(self.root, text="Run Spill Query", command=self.open_spill_query_page)
        self.btn_run_spill_query.pack(side="right", pady=5)

    def get_signals(self):
        self.site_id = int(self.entry_site_id.get())
        site_id = self.site_id
        processor = SiteDataProcessor(
            '../ww_site_info/ww_sites_list.xlsx',
            '../ww_site_info/edm_asset_register.xlsx',
            '../ww_site_info/master_sps_flow_compliance.xlsx'
        )

        rounded_x, rounded_y = processor.get_rounded_coordinates(site_id)
        if rounded_x is not None and rounded_y is not None:
            self.output_text_1.insert(tk.END, f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}\n")
        else:
            self.output_text_1.insert(tk.END, f"SITEID {site_id} not found in the data.\n")

        analogue_server, analogue_signal, spill_mm, pre_spill_mm = processor.get_sump_analogue(site_id)
        if analogue_server is not None and analogue_signal is not None:
            self.output_text_1.insert(tk.END, f"Sump level analogue info for SITEID {site_id}:\n")
            self.output_text_1.insert(tk.END, f"Analogue Server: {analogue_server}\n")
            self.output_text_1.insert(tk.END, f"Analogue Signal: {analogue_signal}\n")
            self.output_text_1.insert(tk.END, f"Spill(mm): {spill_mm}\n")
            self.output_text_1.insert(tk.END, f"Pre-Spill (mm): {pre_spill_mm}\n")
            self.default_spill_level = spill_mm
        else:
            self.output_text_1.insert(tk.END, f"SITEID {site_id} not found in the asset register data.\n")

        queries = processing_functions.read_queries('queries_v3.sql')
        query0 = queries['query0']
        query_formatted_get_signals = query0.format(site_id=site_id)
        df_get_signals = processing_functions.execute_query_and_return_df_site_info("sqlTelemetry", query_formatted_get_signals)
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.tree["column"] = list(df_get_signals.columns)
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        
        df_rows = df_get_signals.to_numpy().tolist()
        for row in df_rows:
            self.tree.insert("", "end", values=row)

        self.filtered_df_rising_main_flow = df_get_signals[df_get_signals['DB Name'].str.contains('rising main flow', case=False, na=False)]
        options = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in self.filtered_df_rising_main_flow.iterrows()] + ["Custom"]
        self.dropdown_var.set("Select flow meter signal")
        self.dropdown_menu['menu'].delete(0, 'end')
        for option in options:
            self.dropdown_menu['menu'].add_command(label=option, command=tk._setit(self.dropdown_var, option))

        self.filtered_df_sump = df_get_signals[df_get_signals['DB Name'].str.contains('sump level', case=False, na=False)]
        options_sump = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in self.filtered_df_sump.iterrows()] + ["Custom"]
        self.dropdown_var_sump.set("Select level analog signal")
        self.dropdown_menu_sump['menu'].delete(0, 'end')
        for option in options_sump:
            self.dropdown_menu_sump['menu'].add_command(label=option, command=tk._setit(self.dropdown_var_sump, option))

    def get_value(self):
        selected_value = self.dropdown_var.get()
        if selected_value == "Custom":
            custom_signal = simpledialog.askstring("Input", "Please enter your custom signal (include the E):")
            custom_source = simpledialog.askstring("Input", "Please enter your custom source :")
            if custom_signal and custom_source:
                self.DB_Addr_rising_main_flow.set(custom_signal)
                self.Source_rising_main_flow.set(custom_source)
            else:
                print("No custom value entered.")
        else:
            db_name, db_addr = selected_value.split(" - ")
            matching_rows = self.filtered_df_rising_main_flow[(self.filtered_df_rising_main_flow['DB Name'] == db_name) & (self.filtered_df_rising_main_flow['DB Addr'] == db_addr)]
            if not matching_rows.empty:
                selected_row = matching_rows.iloc[0]
                self.DB_Addr_rising_main_flow.set(selected_row['DB Addr'])
                self.Source_rising_main_flow.set(selected_row['Source'])
                print(f"Selected DB Addr: {selected_row['DB Addr']}")
                print(f"Selected Source: {selected_row['Source']}")
            else:
                print("No matching rows found in the DataFrame.")

        self.DB_Addr_rising_main_flow_str.set(self.DB_Addr_rising_main_flow.get()[1:])
        self.Source_rising_main_flow_str.set(str(self.Source_rising_main_flow.get()))

    def get_value_sump(self):
            selected_value = self.dropdown_var_sump.get()
            if selected_value == "Custom":
                custom_signal = simpledialog.askstring("Input", "Please enter your custom signal:")
                custom_source = simpledialog.askstring("Input", "Please enter your custom source:")
                if custom_signal and custom_source:
                    self.DB_Addr_sump_var.set(custom_signal)
                    self.Source_sump_var.set(custom_source)
                else:
                    print("No custom value entered.")
            else:
                db_name, db_addr = selected_value.split(" - ")
                matching_rows = self.filtered_df_sump[(self.filtered_df_sump['DB Name'] == db_name) & (self.filtered_df_sump['DB Addr'] == db_addr)]
                if not matching_rows.empty:
                    selected_row = matching_rows.iloc[0]
                    self.DB_Addr_sump_var.set(selected_row['DB Addr'])
                    self.Source_sump_var.set(selected_row['Source'])
                    print(f"Selected DB Addr: {selected_row['DB Addr']}")
                    print(f"Selected Source: {selected_row['Source']}")
                else:
                    print("No matching rows found in the DataFrame.")
            # Create new variables
            self.DB_Addr_sump_str.set(str(self.DB_Addr_sump_var.get())[1:])  # Convert to string and remove the first character
            self.Source_sump_str.set(str(self.Source_sump_var.get()))  # Convert to string

    
    def open_spill_query_page(self):
        spill_query_window = tk.Toplevel(self.root)
        spill_query_window.title("Run Spill Query")
        spill_query_window.configure(bg='light blue')
    
        tk.Label(spill_query_window, text="Enter Spill Level:", bg='light blue').pack(pady=5)
        entry_spill_level = tk.Entry(spill_query_window)
        entry_spill_level.pack(pady=5)
        entry_spill_level.insert(0, str(self.default_spill_level))  # Default value for spill level
    
        tk.Label(spill_query_window, text="Select Start Date:", bg='light blue').pack(pady=5)
        start_date_frame = tk.Frame(spill_query_window, bg='light blue')
        start_date_frame.pack(pady=5)
        start_year = ttk.Combobox(start_date_frame, values=[str(year) for year in range(2000, 2030)])
        start_year.pack(side="left")
        start_year.set("2024")  # Default start year
        start_month = ttk.Combobox(start_date_frame, values=[f"{month:02d}" for month in range(1, 13)])
        start_month.pack(side="left")
        start_month.set("01")  # Default start month
        start_day = ttk.Combobox(start_date_frame, values=[f"{day:02d}" for day in range(1, 32)])
        start_day.pack(side="left")
        start_day.set("01")  # Default start day
    
        tk.Label(spill_query_window, text="Select End Date:", bg='light blue').pack(pady=5)
        end_date_frame = tk.Frame(spill_query_window, bg='light blue')
        end_date_frame.pack(pady=5)
        end_year = ttk.Combobox(end_date_frame, values=[str(year) for year in range(2000, 2030)])
        end_year.pack(side="left")
        end_year.set("2024")  # Default end year
        end_month = ttk.Combobox(end_date_frame, values=[f"{month:02d}" for month in range(1, 13)])
        end_month.pack(side="left")
        end_month.set("10")  # Default end month
        end_day = ttk.Combobox(end_date_frame, values=[f"{day:02d}" for day in range(1, 32)])
        end_day.pack(side="left")
        end_day.set("01")  # Default end day
    
        btn_run_query = tk.Button(spill_query_window, text="Run Query", command=lambda: self.run_spill_query(entry_spill_level.get(), start_year.get(), start_month.get(), start_day.get(), end_year.get(), end_month.get(), end_day.get()))
        btn_run_query.pack(pady=5)



    def run_spill_query(self, spill_level, start_year, start_month, start_day, end_year, end_month, end_day):
        start_date_spill_query = f"{start_year}-{start_month}-{start_day}"
        end_date_spill_query = f"{end_year}-{end_month}-{end_day}"
        queries = processing_functions.read_queries('queries_v3.sql')
        query7 = queries['query7']
        DBAddr_sump = self.DB_Addr_sump_str.get()
        SourceSystem_sump = self.Source_sump_var.get()
        print(start_date_spill_query, end_date_spill_query, DBAddr_sump, SourceSystem_sump)
    
        query_formatted_get_spill_hours = query7.format(start_date_spill_query=start_date_spill_query, end_date_spill_query=end_date_spill_query, DBAddr_sump=DBAddr_sump, SourceSystem_sump=SourceSystem_sump, spill_level=spill_level)
        self.df_spill_hours = processing_functions.execute_query_and_return_df(start_date_spill_query, end_date_spill_query,"sqlTelemetry", query_formatted_get_spill_hours)
        df_spill_hours = self.df_spill_hours
        if df_spill_hours is not None:
           print("Head of df_spill_hours:")
           print(df_spill_hours.head(5))
           df_spill_hours.to_excel(f'../data/raw/site{self.site_id}_from_{start_date_spill_query}_to_{end_date_spill_query}_df_spill_hours.xlsx', index=False)
        # Implement the logic to run the spill query here
        print(f"Running spill query with level: {spill_level}, start date: {start_year}-{start_month}-{start_day}, end date: {end_year}-{end_month}-{end_day}")
       