# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 10:19:12 2024

@author: RMCGINT
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math

# Function to calculate the area of a circle
def calculate_area():
    try:
        radius = float(entry.get())
        area = math.pi * (radius ** 2)
        messagebox.showinfo("Result", f"The area of the circle is: {area:.2f}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")

# Create the main window
root = tk.Tk()
root.geometry("1000x700")
root.title("Circle Area Calculator")
root.resizable(False, False)

# Load and set the window icon
try:
    icon_image = Image.open("..\\logos\\YTL_Logo.png")
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(False, icon_photo)
    print("Image loaded successfully")
except Exception as e:
    print(f"Error loading image: {e}")

# Create and place the widgets
label = tk.Label(root, text="Enter the radius of the circle:")
label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

entry = tk.Entry(root)
entry.grid(row=1, column=0, padx=10, pady=5, sticky="w")

button = tk.Button(root, text="Calculate Area", command=calculate_area)
button.grid(row=2, column=0, padx=10, pady=20, sticky="w")

# Run the application
root.mainloop()
