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
from functions_dal_retrieval import get_value, get_value_sump, open_spill_query_page

        
        
        

# Define global variables for filtered dataframes
filtered_df_rising_main_flow = None
filtered_df_sump = None

# Create the main window
root = tk.Tk()
root.title("Site Information")
root.configure(bg='light blue')

# Create and place the widgets
tk.Label(root, text="Enter Site ID:", bg='light blue').pack(pady=5)
entry_site_id = tk.Entry(root)
entry_site_id.pack(pady=5)

btn_get_signals = tk.Button(root, text="Get Signals", command=lambda: get_signals(entry_site_id, output_text_1, tree, dropdown_var, dropdown_menu, dropdown_var_sump, dropdown_menu_sump))
btn_get_signals.pack(pady=5)

output_text_1 = scrolledtext.ScrolledText(root, width=80, height=10)
output_text_1.pack(pady=5)
output_text_1.configure(bg="light blue")

# Create a frame for the Treeview
frame = tk.Frame(root, bg='light blue')
frame.pack(pady=5)

# Create the Treeview
tree = ttk.Treeview(frame)
tree.pack(side="left")

# Add a scrollbar
scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
scrollbar.pack(side="bottom", fill="x")
tree.configure(xscrollcommand=scrollbar.set)

# Create a frame for the dropdown menus and buttons
right_frame = tk.Frame(root, bg='light blue')
right_frame.pack(side="right", padx=10, pady=10, anchor='ne')

# Create a variable to store the dropdown selection for sump level
dropdown_var_sump = tk.StringVar(value="Select level analog signal")

# Create a dropdown menu for sump level
dropdown_menu_sump = tk.OptionMenu(right_frame, dropdown_var_sump, "Select level analog signal (dropdown)")
dropdown_menu_sump.pack(side="left", pady=5)

# Create a button to confirm the selection for sump level
confirm_button_sump = tk.Button(right_frame, text="Confirm selected level analog", command=lambda: get_value_sump(dropdown_var_sump, filtered_df_sump))
confirm_button_sump.pack(side="right", pady=5)

# Create a variable to store the dropdown selection
dropdown_var = tk.StringVar(value="Select flow meter signal")

# Create a dropdown menu
dropdown_menu = tk.OptionMenu(right_frame, dropdown_var, "Select flow meter signal (dropdown)")
dropdown_menu.pack(side="left", pady=5)

# Create a button to confirm the selection for flow meter signal
confirm_button = tk.Button(right_frame, text="Confirm flow meter signal", command=lambda: get_value(dropdown_var, filtered_df_rising_main_flow))
confirm_button.pack(side="right", pady=5)



# Variables to store the selected DB Addr and Source for flow meter
DB_Addr_rising_main_flow = tk.StringVar()
Source_rising_main_flow = tk.StringVar()

# New variables to store the string conversions for flow meter
DB_Addr_rising_main_flow_str = tk.StringVar()
Source_rising_main_flow_str = tk.StringVar()

# Variables to store the selected DB Addr and Source for sump level
DB_Addr_sump_var = tk.StringVar()
Source_sump_var = tk.StringVar()

# New variables to store the string conversions for sump level
DB_Addr_sump_str = tk.StringVar()
Source_sump_str = tk.StringVar()

btn_run_spill_query = tk.Button(root, text="Run Spill Query", command=open_spill_query_page)
btn_run_spill_query.pack(side="right", pady=5)

root.mainloop()
