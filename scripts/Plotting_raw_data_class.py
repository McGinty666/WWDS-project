# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 15:08:49 2024

@author: RMCGINT
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd



class PlotWindow:
    def __init__(self, root, start_time, end_time, df_raw_sump, spill_level=None, sump_ylim=None):
        self.root = root
        self.root.title("Sump Level Plot")
        
        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)
        self.df_raw_sump = df_raw_sump
        self.spill_level = spill_level
        self.sump_ylim = sump_ylim
        
        self.fig, self.ax1 = plt.subplots(figsize=(12, 6))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.plot_data()
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.BOTTOM)
        
        btn_pan_left = tk.Button(control_frame, text="Pan Left", command=lambda: self.schedule_update('left'))
        btn_pan_left.pack(side=tk.LEFT)
        
        btn_pan_right = tk.Button(control_frame, text="Pan Right", command=lambda: self.schedule_update('right'))
        btn_pan_right.pack(side=tk.LEFT)
        
        btn_zoom_in = tk.Button(control_frame, text="Zoom In", command=self.schedule_zoom_in)
        btn_zoom_in.pack(side=tk.LEFT)
        
        btn_zoom_out = tk.Button(control_frame, text="Zoom Out", command=self.schedule_zoom_out)
        btn_zoom_out.pack(side=tk.LEFT)

    def plot_data(self):
        # Clear the previous plot
        self.ax1.clear()
        
        # Filter the dataframe based on the specified time interval
        df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]

        # Sort the filtered dataframe by time column
        df_sump_filtered = df_sump_filtered.sort_values(by="TimeGMT")

        # Plot sump level on the y-axis
        self.ax1.plot(df_sump_filtered["TimeGMT"], df_sump_filtered["EValue"], color='green', label='Sump Level')
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Sump Level', color='green')
        self.ax1.tick_params(axis='y', labelcolor='green')

        # Apply user-defined axis range if provided
        if self.spill_level:
            self.ax1.set_ylim(0, 1.2 * self.spill_level)

        # Add horizontal line for spill level if provided
        if self.spill_level is not None and isinstance(self.spill_level, (int, float)):
            self.ax1.axhline(y=self.spill_level, color='green', linestyle='--', label='Spill Level')

        # Remove horizontal grid lines
        self.ax1.grid(False)  # Remove horizontal grid lines from the y-axis

        self.fig.tight_layout()
        self.canvas.draw()  # Update the plot in the Tkinter window

    def schedule_update(self, pan_direction):
        self.root.after(100, lambda: self.update_plot(pan_direction))

    def update_plot(self, pan_direction):
        pan_interval = pd.Timedelta(days=30)
        
        if pan_direction == 'left':
            self.start_time -= pan_interval
            self.end_time -= pan_interval
        elif pan_direction == 'right':
            self.start_time += pan_interval
            self.end_time += pan_interval
        
        # Update the plot with new time interval
        self.plot_data()

    def schedule_zoom_in(self):
        self.root.after(100, self.zoom_in)

    def schedule_zoom_out(self):
        self.root.after(100, self.zoom_out)

    def zoom_in(self):
        delta = (self.end_time - self.start_time) / 10
        if (self.end_time - delta > self.start_time + delta):  # Ensure that zooming in doesn't invert the time range.
            self.start_time += delta
            self.end_time -= delta
            self.plot_data()

    def zoom_out(self):
        delta = (self.end_time - self.start_time) / 10
        self.start_time -= delta
        self.end_time += delta
        self.plot_data()

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    
    # Example dataframe (replace with actual data)
    df_raw_sump = pd.DataFrame({
        "TimeGMT": pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "EValue": range(100)
    })
    
    app = PlotWindow(root, "2024-01-01", "2024-01-05", df_raw_sump, spill_level=80)
    root.mainloop()


'''

class PlotWindow:
    def __init__(self, root, start_time, end_time, df_raw_sump, df_rainfall, df_hour_agg_flow_meter, spill_level=None, sump_ylim=None):
        self.root = root
        self.root.title("Rainfall and Flow Meter Plot")
        
        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)
        self.df_raw_sump = df_raw_sump
        self.df_rainfall = df_rainfall
        self.df_hour_agg_flow_meter = df_hour_agg_flow_meter
        self.spill_level = spill_level
        self.sump_ylim = sump_ylim
        
        self.fig, self.ax1 = plt.subplots(figsize=(12, 6))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.plot_data()
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.BOTTOM)
        
        btn_pan_left = tk.Button(control_frame, text="Pan Left", command=lambda: self.update_plot('left'))
        btn_pan_left.pack(side=tk.LEFT)
        
        btn_pan_right = tk.Button(control_frame, text="Pan Right", command=lambda: self.update_plot('right'))
        btn_pan_right.pack(side=tk.LEFT)
        
        btn_zoom_in = tk.Button(control_frame, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.pack(side=tk.LEFT)
        
        btn_zoom_out = tk.Button(control_frame, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.pack(side=tk.LEFT)

    def plot_data(self):
        # Clear the previous plot
        self.ax1.clear()
        
        # Filter the dataframes based on the specified time interval
        df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]
        df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= self.start_time) & (self.df_rainfall["time_gmt_n"] <= self.end_time)]
        df_hour_agg_flow_meter_filtered = self.df_hour_agg_flow_meter[
            (pd.to_datetime(self.df_hour_agg_flow_meter["Year"].astype(str) + '-' + self.df_hour_agg_flow_meter["Month"].astype(str) + '-' + self.df_hour_agg_flow_meter["Day"].astype(str) + ' ' + self.df_hour_agg_flow_meter["Hour"].astype(str) + ':00:00') >= self.start_time) & 
            (pd.to_datetime(self.df_hour_agg_flow_meter["Year"].astype(str) + '-' + self.df_hour_agg_flow_meter["Month"].astype(str) + '-' + self.df_hour_agg_flow_meter["Day"].astype(str) + ' ' + self.df_hour_agg_flow_meter["Hour"].astype(str) + ':00:00') <= self.end_time)
        ]

        # Sort the filtered dataframes by their respective time columns
        df_sump_filtered = df_sump_filtered.sort_values(by="TimeGMT")
        df_rainfall_filtered = df_rainfall_filtered.sort_values(by="time_gmt_n")
        df_hour_agg_flow_meter_filtered = df_hour_agg_flow_meter_filtered.sort_values(by=["Year", "Month", "Day", "Hour"])

        # Plot sump level on the first y-axis
        self.ax1.plot(df_sump_filtered["TimeGMT"], df_sump_filtered["EValue"], color='green', label='Sump Level')
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Sump Level', color='green')
        self.ax1.tick_params(axis='y', labelcolor='green')

        # Apply user-defined axis range if provided
        if self.spill_level:
            self.ax1.set_ylim(0, 1.2 * self.spill_level)

        # Add horizontal line for spill level if provided
        if self.spill_level is not None and isinstance(self.spill_level, (int, float)):
            self.ax1.axhline(y=self.spill_level, color='green', linestyle='--', label='Spill Level')

        # Create a second y-axis for rainfall
        ax2 = self.ax1.twinx()
        ax2.bar(df_rainfall_filtered["time_gmt_n"], df_rainfall_filtered["Intensity(mm/hr)"], color='blue', label='Rainfall', width=0.01)
        ax2.set_ylabel('Rainfall intensity (mm/h)', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        # Set a fixed range for rainfall intensity axis
        ax2.set_ylim(0, 100)

        # Create a third y-axis for meanEValue
        ax3 = self.ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))  # Offset the third axis to the right
        ax3.plot(
            pd.to_datetime(df_hour_agg_flow_meter_filtered["Year"].astype(str) + '-' + df_hour_agg_flow_meter_filtered["Month"].astype(str) + '-' + df_hour_agg_flow_meter_filtered["Day"].astype(str) + ' ' + df_hour_agg_flow_meter_filtered["Hour"].astype(str) + ':00:00'), 
            df_hour_agg_flow_meter_filtered["meanEValue"], color='red', label='Mean EValue'
        )
        ax3.set_ylabel('Mean EValue flow meter', color='red')
        ax3.tick_params(axis='y', labelcolor='red')
        
        # Set a fixed range for mean EValue flow meter axis
        ax3.set_ylim(0, 100)

        # Add title and remove horizontal grid lines
        plt.title(f'Nearby Rainfall, Sump Level, and Mean EValue flow meter from {self.start_time} to {self.end_time}')
        self.ax1.grid(False)  # Remove horizontal grid lines from the first y-axis
        ax2.grid(False)  # Remove horizontal grid lines from the second y-axis
        ax3.grid(False)  # Remove horizontal grid lines from the third y-axis

        self.fig.tight_layout()
        self.canvas.draw()  # Update the plot in the Tkinter window

    def update_plot(self, pan_direction):
        pan_interval = pd.Timedelta(days=30)
        
        if pan_direction == 'left':
            self.start_time -= pan_interval
            self.end_time -= pan_interval
        elif pan_direction == 'right':
            self.start_time += pan_interval
            self.end_time += pan_interval
        
        # Update the plot with new time interval
        self.plot_data()

    def zoom_in(self):
        delta = (self.end_time - self.start_time) / 10
        if (self.end_time - delta > self.start_time + delta):  # Ensure that zooming in doesn't invert the time range.
            self.start_time += delta
            self.end_time -= delta
            self.plot_data()

    def zoom_out(self):
        delta = (self.end_time - self.start_time) / 10
        self.start_time -= delta
        self.end_time += delta
        self.plot_data()

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    
    # Example dataframes (replace with actual data)
    df_raw_sump = pd.DataFrame({
        "TimeGMT": pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "EValue": range(100)
    })
    df_rainfall = pd.DataFrame({
        "time_gmt_n": pd.date_range(start="2024-01-01", periods=100, freq="H"),
        "Intensity(mm/hr)": range(100)
    })
    df_hour_agg_flow_meter = pd.DataFrame({
        "Year": [2024]*100,
        "Month": [1]*100,
        "Day": list(range(1, 101)),
        "Hour": [0]*100,
        "meanEValue": range(100)
    })
    
    app = PlotWindow(root, "2024-01-01", "2024-01-05", df_raw_sump, df_rainfall, df_hour_agg_flow_meter, spill_level=80)
    root.mainloop()



'''


