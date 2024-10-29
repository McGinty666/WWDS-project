# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 21:44:13 2024

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
import tkinter as tk
from Class_tkinter import SiteInformationApp  # Assuming your class is in a file named site_information_app.py

if __name__ == "__main__":
    root = tk.Tk()
    app = SiteInformationApp(root)
    root.mainloop()