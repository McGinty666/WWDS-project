import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

class PlotWindow:
    def __init__(self, root, start_time, end_time, df_raw_sump, df_rainfall=None, df_hour_agg_flow_meter=None, spill_level=None, sump_ylim=None):
        self.root = root
        self.root.title("Rainfall and Flow Meter Plot")

        self.start_time = pd.to_datetime(start_time)
        self.end_time = pd.to_datetime(end_time)

        # Assign dataframes to instance variables
        self.df_raw_sump = df_raw_sump
        self.df_rainfall = df_rainfall
        self.df_hour_agg_flow_meter = df_hour_agg_flow_meter

        # Pre-filter data for efficiency
        self.df_sump_filtered = df_raw_sump[(df_raw_sump["TimeGMT"] >= self.start_time) & (df_raw_sump["TimeGMT"] <= self.end_time)]
        self.df_rainfall_filtered = df_rainfall[(df_rainfall["time_gmt_n"] >= self.start_time) & (df_rainfall["time_gmt_n"] <= self.end_time)] if df_rainfall is not None else None
        self.df_flow_meter_filtered = df_hour_agg_flow_meter[(df_hour_agg_flow_meter["TimeGMT"] >= self.start_time) & (df_hour_agg_flow_meter["TimeGMT"] <= self.end_time)] if df_hour_agg_flow_meter is not None else None

        self.spill_level = spill_level
        self.sump_ylim = sump_ylim

        self.fig = Figure(figsize=(12, 8))
        self.ax1, self.ax2, self.ax3 = self.fig.subplots(3, 1, sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.plot_data(initial=True)  # Initial plot with pre-filtered data

        # Control frame and buttons
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
        
        # Add this in the __init__ method of PlotWindow class
        btn_remove_dwf = tk.Button(control_frame, text="Remove DWF", command=self.open_remove_dwf_window)
        btn_remove_dwf.pack(side=tk.LEFT)

    def plot_data(self, initial=False):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
    
        # Use pre-filtered dataframes
        df_sump = self.df_sump_filtered
        df_rain = self.df_rainfall_filtered
        df_flow = self.df_flow_meter_filtered
    
        # Plot rainfall
        if df_rain is not None and not df_rain.empty:
            self.ax1.bar(df_rain["time_gmt_n"], df_rain["Intensity(mm/hr)"], color='blue', label='Rainfall', width=0.01, alpha=0.5)
            self.ax1.set_ylabel('Rainfall intensity (mm/h)', color='blue')
            self.ax1.tick_params(axis='y', labelcolor='blue')
            self.ax1.set_ylim(2, 0)  # Inverted axis
    
        # Plot flow meter data
        if df_flow is not None and not df_flow.empty:
            self.ax2.plot(df_flow["TimeGMT"], df_flow["meanEValue"], color='red', label='Mean EValue')
            self.ax2.set_ylabel('Mean EValue flow meter', color='red')
            self.ax2.tick_params(axis='y', labelcolor='red')
            self.ax2.set_ylim(0, 100)
            self.plot_adjusted_flow_meter()  # Add this line
    
        # Plot sump level
        if not df_sump.empty:
            self.ax3.plot(df_sump["TimeGMT"], df_sump["EValue"], color='green', label='Sump Level')
            self.ax3.set_ylabel('Sump Level', color='green')
            self.ax3.tick_params(axis='y', labelcolor='green')
    
        # Spill level
        if self.spill_level:
            self.ax3.set_ylim(0, 1.2 * self.spill_level)
            self.ax3.axhline(y=self.spill_level, color='green', linestyle='--', label='Spill Level')
    
        self.ax3.set_xlabel('Time')
        self.fig.suptitle('Rainfall, Flow Meter, and Sump Level')
        self.fig.tight_layout()
        self.canvas.draw()



    def update_plot(self, pan_direction):
        pan_interval = pd.Timedelta(days=2)

        if pan_direction == 'left':
            self.start_time -= pan_interval
            self.end_time -= pan_interval
        elif pan_direction == 'right':
            self.start_time += pan_interval
            self.end_time += pan_interval

        # Re-filter data for the new time range
        self.df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]
        if self.df_rainfall is not None:
            self.df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= self.start_time) & (self.df_rainfall["time_gmt_n"] <= self.end_time)]
        if self.df_hour_agg_flow_meter is not None:
            self.df_flow_meter_filtered = self.df_hour_agg_flow_meter[(self.df_hour_agg_flow_meter["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter["TimeGMT"] <= self.end_time)]

        self.plot_data()

    def zoom_in(self):
        delta = (self.end_time - self.start_time) / 10
        if (self.end_time - delta > self.start_time + delta):
            self.start_time += delta
            self.end_time -= delta

            # Re-filter data for the new time range
            self.df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]
            if self.df_rainfall is not None:
                self.df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= self.start_time) & (self.df_rainfall["time_gmt_n"] <= self.end_time)]
            if self.df_hour_agg_flow_meter is not None:
                self.df_flow_meter_filtered = self.df_hour_agg_flow_meter[(self.df_hour_agg_flow_meter["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter["TimeGMT"] <= self.end_time)]

            self.plot_data()

    def zoom_out(self):
        delta = (self.end_time - self.start_time) / 10
        self.start_time -= delta
        self.end_time += delta

        # Re-filter data for the new time range
        self.df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]
        if self.df_rainfall is not None:
            self.df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= self.start_time) & (self.df_rainfall["time_gmt_n"] <= self.end_time)]
        if self.df_hour_agg_flow_meter is not None:
            self.df_flow_meter_filtered = self.df_hour_agg_flow_meter[(self.df_hour_agg_flow_meter["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter["TimeGMT"] <= self.end_time)]

        self.plot_data()
        

    
    # Add these methods to the PlotWindow class
    def open_remove_dwf_window(self):
        self.remove_dwf_window = tk.Toplevel(self.root)
        self.remove_dwf_window.title("Remove DWF")
    
        tk.Label(self.remove_dwf_window, text="Start Date:").grid(row=0, column=0)
        tk.Label(self.remove_dwf_window, text="End Date:").grid(row=1, column=0)
    
        self.start_year = ttk.Combobox(self.remove_dwf_window, values=[str(year) for year in range(2000, 2031)])
        self.start_month = ttk.Combobox(self.remove_dwf_window, values=[str(month).zfill(2) for month in range(1, 13)])
        self.start_day = ttk.Combobox(self.remove_dwf_window, values=[str(day).zfill(2) for day in range(1, 32)])
        self.end_year = ttk.Combobox(self.remove_dwf_window, values=[str(year) for year in range(2000, 2031)])
        self.end_month = ttk.Combobox(self.remove_dwf_window, values=[str(month).zfill(2) for month in range(1, 13)])
        self.end_day = ttk.Combobox(self.remove_dwf_window, values=[str(day).zfill(2) for day in range(1, 32)])
    
        self.start_year.grid(row=0, column=1)
        self.start_month.grid(row=0, column=2)
        self.start_day.grid(row=0, column=3)
        self.end_year.grid(row=1, column=1)
        self.end_month.grid(row=1, column=2)
        self.end_day.grid(row=1, column=3)
    
        self.start_year.current(0)
        self.start_month.current(0)
        self.start_day.current(0)
        self.end_year.current(0)
        self.end_month.current(0)
        self.end_day.current(0)
    
        btn_apply = tk.Button(self.remove_dwf_window, text="Apply", command=self.calculate_median_profile)
        btn_apply.grid(row=2, column=0, columnspan=4)
    
    def calculate_median_profile(self):


        start_date = f"{self.start_year.get()}-{self.start_month.get()}-{self.start_day.get()}"
        end_date = f"{self.end_year.get()}-{self.end_month.get()}-{self.end_day.get()}"
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    
        df_filtered = self.df_hour_agg_flow_meter[(self.df_hour_agg_flow_meter["TimeGMT"] >= start_date) & (self.df_hour_agg_flow_meter["TimeGMT"] <= end_date)].copy()
        df_filtered.loc[:, 'Hour'] = df_filtered['TimeGMT'].dt.hour
        median_profile = df_filtered.groupby('Hour')['meanEValue'].median()
    
        self.plot_median_profile(median_profile)
        
        self.median_profile = median_profile
        self.subtract_median_profile()

        self.median_profile = median_profile
        self.subtract_median_profile_from_dataset()
        


    
    def plot_median_profile(self, median_profile):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(median_profile.index, median_profile.values, marker='o', linestyle='-')
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel('Median EValue')
        ax.set_title('Median EValue Flow Meter Profile')
    
        canvas = FigureCanvasTkAgg(fig, master=self.remove_dwf_window)
        canvas.get_tk_widget().grid(row=3, column=0, columnspan=4)
        canvas.draw()       
            
    def subtract_median_profile(self):
        if self.df_flow_meter_filtered is not None and not self.df_flow_meter_filtered.empty:
            df_copy = self.df_flow_meter_filtered.copy()
            df_copy['Hour'] = df_copy['TimeGMT'].dt.hour
            df_copy['AdjustedEValue'] = df_copy.apply(lambda row: row['meanEValue'] - self.median_profile.get(row['Hour'], 0), axis=1)
            self.df_flow_meter_adjusted = df_copy

    def plot_adjusted_flow_meter(self):
        if hasattr(self, 'df_flow_meter_adjusted') and not self.df_flow_meter_adjusted.empty:
            self.ax2.plot(self.df_flow_meter_adjusted["TimeGMT"], self.df_flow_meter_adjusted["AdjustedEValue"], color='purple', label='Adjusted EValue')
            self.ax2.legend()
    

            
    def subtract_median_profile_from_dataset(self):
        if self.df_hour_agg_flow_meter is not None and not self.df_hour_agg_flow_meter.empty:
            df_copy = self.df_hour_agg_flow_meter.copy()
            df_copy['Hour'] = df_copy['TimeGMT'].dt.hour
            df_copy['AdjustedEValue'] = df_copy.apply(lambda row: row['meanEValue'] - self.median_profile.get(row['Hour'], 0), axis=1)
            self.df_hour_agg_flow_meter_adjusted = df_copy
    
    def plot_adjusted_flow_meter(self):
        if hasattr(self, 'df_hour_agg_flow_meter_adjusted') and not self.df_hour_agg_flow_meter_adjusted.empty:
            df_adjusted_filtered = self.df_hour_agg_flow_meter_adjusted[(self.df_hour_agg_flow_meter_adjusted["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter_adjusted["TimeGMT"] <= self.end_time)]
            self.ax2.plot(df_adjusted_filtered["TimeGMT"], df_adjusted_filtered["AdjustedEValue"], color='purple', label='Adjusted EValue')
            self.ax2.legend()
        
            
        
        

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotWindow(root, "2024-10-01", "2024-10-20", df_raw_sump=df_sump_filtered, df_rainfall=df_rainfall_filtered, df_hour_agg_flow_meter=df_hour_agg_flow_meter_filtered, spill_level=95, sump_ylim=100)
    root.mainloop()
