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
import tkinter as tk
from tkinter import messagebox
import math
from functions_dal_retrieval import get_signals, get_value, get_value_sump



'''
def get_signals():
    site_id = int(entry_site_id.get())
    processor = SiteDataProcessor(
        '../ww_site_info/ww_sites_list.xlsx',
        '../ww_site_info/edm_asset_register.xlsx',
        '../ww_site_info/master_sps_flow_compliance.xlsx'
    )

    rounded_x, rounded_y = processor.get_rounded_coordinates(site_id)
    if rounded_x is not None and rounded_y is not None:
        output_text_1.insert(tk.END, f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}\n")
    else:
        output_text_1.insert(tk.END, f"SITEID {site_id} not found in the data.\n")

    analogue_server, analogue_signal, spill_mm, pre_spill_mm = processor.get_sump_analogue(site_id)
    if analogue_server is not None and analogue_signal is not None:
        output_text_1.insert(tk.END, f"Sump level analogue info for SITEID {site_id}:\n")
        output_text_1.insert(tk.END, f"Analogue Server: {analogue_server}\n")
        output_text_1.insert(tk.END, f"Analogue Signal: {analogue_signal}\n")
        output_text_1.insert(tk.END, f"Spill(mm): {spill_mm}\n")
        output_text_1.insert(tk.END, f"Pre-Spill (mm): {pre_spill_mm}\n")
    else:
        output_text_1.insert(tk.END, f"SITEID {site_id} not found in the asset register data.\n")

    queries = processing_functions.read_queries('queries_v3.sql')
    query0 = queries['query0']
    query_formatted_get_signals = query0.format(site_id=site_id)
    df_get_signals = processing_functions.execute_query_and_return_df_site_info("sqlTelemetry", query_formatted_get_signals)
    
    # Clear the Treeview
    for i in tree.get_children():
        tree.delete(i)
    
    # Insert new data into the Treeview
    tree["column"] = list(df_get_signals.columns)
    tree["show"] = "headings"
    for col in tree["columns"]:
        tree.heading(col, text=col)
    
    df_rows = df_get_signals.to_numpy().tolist()
    for row in df_rows:
        tree.insert("", "end", values=row)

    # Filter the dataframe for 'rising main flow'
    global filtered_df_rising_main_flow
    filtered_df_rising_main_flow = df_get_signals[df_get_signals['DB Name'].str.contains('rising main flow', case=False, na=False)]
    options = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in filtered_df_rising_main_flow.iterrows()] + ["Custom"]
    dropdown_var.set("Select flow meter signal")
    dropdown_menu['menu'].delete(0, 'end')
    for option in options:
        dropdown_menu['menu'].add_command(label=option, command=tk._setit(dropdown_var, option))

    # Filter the dataframe for 'sump level'
    global filtered_df_sump
    filtered_df_sump = df_get_signals[df_get_signals['DB Name'].str.contains('sump level', case=False, na=False)]
    options_sump = [f"{row['DB Name']} - {row['DB Addr']}" for index, row in filtered_df_sump.iterrows()] + ["Custom"]
    dropdown_var_sump.set("Select level analog signal")
    dropdown_menu_sump['menu'].delete(0, 'end')
    for option in options_sump:
        dropdown_menu_sump['menu'].add_command(label=option, command=tk._setit(dropdown_var_sump, option))

def get_value():
    selected_value = dropdown_var.get()
    if selected_value == "Custom":
        custom_signal = simpledialog.askstring("Input", "Please enter your custom signal (include the E):")
        custom_source = simpledialog.askstring("Input", "Please enter your custom source :")
        if custom_signal and custom_source:
            DB_Addr_rising_main_flow.set(custom_signal)
            Source_rising_main_flow.set(custom_source)
        else:
            print("No custom value entered.")
    else:
        db_name, db_addr = selected_value.split(" - ")
        matching_rows = filtered_df_rising_main_flow[(filtered_df_rising_main_flow['DB Name'] == db_name) & (filtered_df_rising_main_flow['DB Addr'] == db_addr)]
        if not matching_rows.empty:
            selected_row = matching_rows.iloc[0]
            DB_Addr_rising_main_flow.set(selected_row['DB Addr'])
            Source_rising_main_flow.set(selected_row['Source'])
            print(f"Selected DB Addr: {selected_row['DB Addr']}")
            print(f"Selected Source: {selected_row['Source']}")
        else:
            print("No matching rows found in the DataFrame.")

    # Create new variables
    DB_Addr_rising_main_flow_str.set(DB_Addr_rising_main_flow.get()[1:])  # Convert to string and remove the first character
    Source_rising_main_flow_str.set(str(Source_rising_main_flow.get()))  # Convert to string

def get_value_sump():
    selected_value = dropdown_var_sump.get()
    if selected_value == "Custom":
        custom_signal = simpledialog.askstring("Input", "Please enter your custom signal:")
        custom_source = simpledialog.askstring("Input", "Please enter your custom source:")
        if custom_signal and custom_source:
            DB_Addr_sump_var.set(custom_signal)
            Source_sump_var.set(custom_source)
        else:
            print("No custom value entered.")
    else:
        db_name, db_addr = selected_value.split(" - ")
        matching_rows = filtered_df_sump[(filtered_df_sump['DB Name'] == db_name) & (filtered_df_sump['DB Addr'] == db_addr)]
        if not matching_rows.empty:
            selected_row = matching_rows.iloc[0]
            DB_Addr_sump_var.set(selected_row['DB Addr'])
            Source_sump_var.set(selected_row['Source'])
            print(f"Selected DB Addr: {selected_row['DB Addr']}")
            print(f"Selected Source: {selected_row['Source']}")
        else:
            print("No matching rows found in the DataFrame.")

    # Create new variables
    DB_Addr_sump_str.set(str(DB_Addr_sump_var.get())[1:])  # Convert to string and remove the first character
    Source_sump_str.set(str(Source_sump_var.get()))  # Convert to string

'''
# Create the main window
root = tk.Tk()
root.title("Site Information")
root.configure(bg='light blue')

# Create and place the widgets
tk.Label(root, text="Enter Site ID:", bg='light blue').pack(pady=5)
entry_site_id = tk.Entry(root)
entry_site_id.pack(pady=5)

btn_get_signals = tk.Button(root, text="Get Signals", command=get_signals)
btn_get_signals.pack(pady=5)

output_text_1 = scrolledtext.ScrolledText(root, width=80, height=10)
output_text_1.pack(pady=5)

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

# Create a variable to store the dropdown selection
dropdown_var = tk.StringVar(value="Select flow meter signal")

# Create a dropdown menu
dropdown_menu = tk.OptionMenu(right_frame, dropdown_var, "Select flow meter signal (dropdown)")
dropdown_menu.pack(side="top", pady=5)

# Create a button to confirm the selection
confirm_button = tk.Button(right_frame, text="Confirm flow meter signal", command=get_value)
confirm_button.pack(side="top", pady=5)

# Create a variable to store the dropdown selection for sump level
dropdown_var_sump = tk.StringVar(value="Select level analog signal")

# Create a dropdown menu for sump level
dropdown_menu_sump = tk.OptionMenu(right_frame, dropdown_var_sump, "Select level analog signal (dropdown)")
dropdown_menu_sump.pack(side="top", pady=5)

# Create a button to confirm the selection for sump level
confirm_button_sump = tk.Button(right_frame, text="Confirm selected level analog", command=get_value_sump)
confirm_button_sump.pack(side="top", pady=5)

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

# Load and set the window icon
icon_image = Image.open("..\\logos\\sklt.png")
icon_photo = ImageTk.PhotoImage(icon_image)
root.iconphoto(False, icon_photo)


# Run the application
root.mainloop()

