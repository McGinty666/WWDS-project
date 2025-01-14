import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error
import numpy as np


class PlotWindow:
    def __init__(self, root, start_time, end_time, df_raw_sump, df_rainfall=None, df_hour_agg_flow_meter=None, spill_level=None, sump_ylim=None, flow_ylim=None):
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
    
        self.rainfall_values = df_rainfall
    
        self.spill_level = spill_level
        self.sump_ylim = sump_ylim
        self.flow_ylim =flow_ylim
    
        self.fig = Figure(figsize=(12, 8))
        self.ax1, self.ax2, self.ax3 = self.fig.subplots(3, 1, sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        
        # Initialize RTK parameters and synthetic flow
        self.R1 = None
        self.T1 = None
        self.K1 = None
        self.R2 = None
        self.T2 = None
        self.K2 = None
        self.df_synthetic_flow = None
            
    
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
    
        btn_optimize_rtk = tk.Button(control_frame, text="Optimize RTK", command=self.open_optimize_rtk_window)
        btn_optimize_rtk.pack(side=tk.LEFT)
    
        # Add a text box for pan speed
        self.pan_speed_var = tk.StringVar(value="7")  # Default pan speed is 2 days
        lbl_pan_speed = tk.Label(control_frame, text="Pan Speed (days):")
        lbl_pan_speed.pack(side=tk.LEFT)
        txt_pan_speed = tk.Entry(control_frame, textvariable=self.pan_speed_var, width=5)
        txt_pan_speed.pack(side=tk.LEFT)
        
         # Add a text box and button for skipping to a particular date
        lbl_skip_date = tk.Label(control_frame, text="Skip to Date (YYYY-MM-DD):")
        lbl_skip_date.pack(side=tk.LEFT)
        
        self.skip_date_var = tk.StringVar()
        txt_skip_date = tk.Entry(control_frame, textvariable=self.skip_date_var, width=10)
        txt_skip_date.pack(side=tk.LEFT)
       
        btn_skip_date = tk.Button(control_frame, text="Go", command=self.skip_to_date)
        btn_skip_date.pack(side=tk.LEFT)
     



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
            self.ax1.bar(df_rain["time_gmt_n"], df_rain["Intensity(mm/hr)"], color='blue', label='Rainfall', width=0.12, alpha=0.5)
            self.ax1.set_ylabel('Rainfall intensity (mm/h)', color='blue')
            self.ax1.tick_params(axis='y', labelcolor='blue')
            self.ax1.set_ylim(3, 0)  # Inverted axis
    
        # Plot flow meter data
        if df_flow is not None and not df_flow.empty:
            self.ax2.plot(df_flow["TimeGMT"], df_flow["flow_trend"], color='red', label='Mean EValue')
            self.ax2.set_ylabel('Mean EValue flow meter', color='red')
            self.ax2.tick_params(axis='y', labelcolor='red')
            self.ax2.set_ylim(0, self.flow_ylim)
            self.plot_adjusted_flow_meter()  # Add this line

        # Plot flow meter data
        #if df_flow is not None and not df_flow.empty:
            #self.ax2.plot(df_flow["TimeGMT"], df_flow["meanEValue"], color='green', label='flow_trend')
            #self.ax2.set_ylabel('Mean EValue flow meter', color='green')
            #self.ax2.tick_params(axis='y', labelcolor='green')
            #self.ax2.set_ylim(0, self.flow_ylim)
            #self.plot_adjusted_flow_meter()  # Add this line
    
        # Plot sump level
        if not df_sump.empty:
            self.ax3.plot(df_sump["TimeGMT"], df_sump["EValue"], color='green', label='Sump Level')
            self.ax3.set_ylabel('Sump Level', color='green')
            self.ax3.tick_params(axis='y', labelcolor='green')
    
        # Spill level
        if self.spill_level:
            self.ax3.set_ylim(0, 1.2 * self.spill_level)
            self.ax3.axhline(y=self.spill_level, color='green', linestyle='--', label='Spill Level')
    
        # Plot synthetic flow if available
        if self.df_synthetic_flow is not None and not self.df_synthetic_flow.empty:  # Updated check
            df_synthetic_filtered = self.df_synthetic_flow[(self.df_synthetic_flow["TimeGMT"] >= self.start_time) & (self.df_synthetic_flow["TimeGMT"] <= self.end_time)]
            if not df_synthetic_filtered.empty:
                print("Plotting synthetic flow")  # Debugging line to check if this block is executed
                print(df_synthetic_filtered.head())  # Debugging line to check the content of the DataFrame
                print(self.start_time, "to", self.end_time)  # Debugging line to check the time range being used for filtering
                print(self.df_synthetic_flow.head())  # Debugging line to check the content of the original DataFrame before filtering
                # Plot synthetic flow in black
                self.ax2.plot(df_synthetic_filtered["TimeGMT"], df_synthetic_filtered["SyntheticFlow"], color='black', label='Synthetic Flow')
                self.ax2.legend()
                
            # Highlight the training period
        if hasattr(self, 'training_start_time') and hasattr(self, 'training_end_time'):
            self.ax2.axvspan(self.training_start_time, self.training_end_time, color='yellow', alpha=0.3, label='Training Period')
            self.ax2.legend()
        
        self.ax3.set_xlabel('Time')
        self.fig.suptitle('Rainfall, Flow Meter, and Sump Level')
        self.fig.tight_layout()
        self.canvas.draw()
    



    def update_plot(self, pan_direction):
        try:
            pan_interval_days = int(self.pan_speed_var.get())
        except ValueError:
            pan_interval_days = 7  # Default to 7 days if input is invalid
    
        pan_interval = pd.Timedelta(days=pan_interval_days)
    
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
        
    def skip_to_date(self):
        try:
            skip_date = pd.to_datetime(self.skip_date_var.get())
            self.start_time = skip_date
            self.end_time = skip_date + (self.end_time - self.start_time)

            # Re-filter data based on the new time range
            self.df_sump_filtered = self.df_raw_sump[(self.df_raw_sump["TimeGMT"] >= self.start_time) & (self.df_raw_sump["TimeGMT"] <= self.end_time)]
            self.df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= self.start_time) & (self.df_rainfall["time_gmt_n"] <= self.end_time)] if self.df_rainfall is not None else None
            self.df_flow_meter_filtered = self.df_hour_agg_flow_meter[(self.df_hour_agg_flow_meter["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter["TimeGMT"] <= self.end_time)] if self.df_hour_agg_flow_meter is not None else None

            # Update the plot with the new data
            self.plot_data()
        except ValueError:
            print("Invalid date format. Please enter a date in YYYY-MM-DD format.")


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
            df_copy['AdjustedEValue'] = df_copy.apply(lambda row: row['flow_trend'] - self.median_profile.get(row['Hour'], 0), axis=1)
            self.df_flow_meter_adjusted = df_copy


            
    def subtract_median_profile_from_dataset(self):
        if self.df_hour_agg_flow_meter is not None and not self.df_hour_agg_flow_meter.empty:
            df_copy = self.df_hour_agg_flow_meter.copy()
            df_copy['Hour'] = df_copy['TimeGMT'].dt.hour
            df_copy['AdjustedEValue'] = df_copy.apply(lambda row: row['flow_trend'] - self.median_profile.get(row['Hour'], 0), axis=1)
            self.df_hour_agg_flow_meter_adjusted = df_copy
    
    def plot_adjusted_flow_meter(self):
        if hasattr(self, 'df_hour_agg_flow_meter_adjusted') and not self.df_hour_agg_flow_meter_adjusted.empty:
            df_adjusted_filtered = self.df_hour_agg_flow_meter_adjusted[(self.df_hour_agg_flow_meter_adjusted["TimeGMT"] >= self.start_time) & (self.df_hour_agg_flow_meter_adjusted["TimeGMT"] <= self.end_time)]
            self.ax2.plot(df_adjusted_filtered["TimeGMT"], df_adjusted_filtered["AdjustedEValue"], color='purple', label='Adjusted EValue')
            self.ax2.legend()

        
    def open_optimize_rtk_window(self):
        self.optimize_rtk_window = tk.Toplevel(self.root)
        self.optimize_rtk_window.title("Optimize RTK Parameters")
        
        tk.Label(self.optimize_rtk_window, text="Start Date:").grid(row=0, column=0)
        tk.Label(self.optimize_rtk_window, text="End Date:").grid(row=1, column=0)
        
        self.train_start_year = ttk.Combobox(self.optimize_rtk_window, values=[str(year) for year in range(2000, 2031)])
        self.train_start_month = ttk.Combobox(self.optimize_rtk_window, values=[str(month).zfill(2) for month in range(1, 13)])
        self.train_start_day = ttk.Combobox(self.optimize_rtk_window, values=[str(day).zfill(2) for day in range(1, 32)])
        self.train_end_year = ttk.Combobox(self.optimize_rtk_window, values=[str(year) for year in range(2000, 2031)])
        self.train_end_month = ttk.Combobox(self.optimize_rtk_window, values=[str(month).zfill(2) for month in range(1, 13)])
        self.train_end_day = ttk.Combobox(self.optimize_rtk_window, values=[str(day).zfill(2) for day in range(1, 32)])
        
        self.train_start_year.grid(row=0, column=1)
        self.train_start_month.grid(row=0, column=2)
        self.train_start_day.grid(row=0, column=3)
        self.train_end_year.grid(row=1, column=1)
        self.train_end_month.grid(row=1, column=2)
        self.train_end_day.grid(row=1, column=3)
        
        # Set default dates
        self.train_start_year.set("2023")
        self.train_start_month.set("07")
        self.train_start_day.set("23")
        self.train_end_year.set("2023")
        self.train_end_month.set("08")
        self.train_end_day.set("10")
        
        
        btn_apply = tk.Button(self.optimize_rtk_window, text="Apply", command=self.fit_rtk_parameters)
        btn_apply.grid(row=2, column=0, columnspan=4)

    def fit_rtk_parameters(self):
        start_date = f"{self.train_start_year.get()}-{self.train_start_month.get()}-{self.train_start_day.get()}"
        end_date = f"{self.train_end_year.get()}-{self.train_end_month.get()}-{self.train_end_day.get()}"
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    
        df_rainfall_filtered = self.df_rainfall[(self.df_rainfall["time_gmt_n"] >= start_date) & (self.df_rainfall["time_gmt_n"] <= end_date)]
        df_flow_filtered = self.df_hour_agg_flow_meter_adjusted[(self.df_hour_agg_flow_meter_adjusted["TimeGMT"] >= start_date) & (self.df_hour_agg_flow_meter_adjusted["TimeGMT"] <= end_date)]
    
        # Ensure the dataframes are aligned by time
        df_rainfall_filtered.set_index("time_gmt_n", inplace=True)
        df_flow_filtered.set_index("TimeGMT", inplace=True)
    
        # Reindex to the same time index, filling missing values in rainfall with 0
        common_index = df_flow_filtered.index.union(df_rainfall_filtered.index)
        
        # Ensure that common_index is not empty before proceeding
        if common_index.empty:
            print("No common time points available for the selected period.")
            return
        
        df_rainfall_filtered = df_rainfall_filtered.reindex(common_index, fill_value=0)
        df_flow_filtered = df_flow_filtered.reindex(common_index)
    
                # Check if 'AdjustedEValue' column exists before attempting to fill NaN values

        df_flow_filtered["AdjustedEValue"] = df_flow_filtered["AdjustedEValue"].fillna(df_flow_filtered["AdjustedEValue"].mean())

    
        # Ensure that the reindexed dataframes do not contain NaN values before proceeding
        if df_flow_filtered["AdjustedEValue"].isna().any() or df_rainfall_filtered["Intensity(mm/hr)"].isna().any():
            print("Reindexed data contains NaN values.")
            return
    
        self.rainfall_values = df_rainfall_filtered["Intensity(mm/hr)"].values
        self.flow_values = df_flow_filtered["AdjustedEValue"].values
    
        # Ensure that flow_values and rainfall_values are not empty before proceeding
        if len(self.flow_values) == 0 or len(self.rainfall_values) == 0:
            print("No flow or rainfall data available for the selected period.")
            return
    
        # Ensure that flow_values and rainfall_values do not contain NaN or infinite values before proceeding
        if np.isnan(self.flow_values).any() or np.isnan(self.rainfall_values).any() or np.isinf(self.flow_values).any() or np.isinf(self.rainfall_values).any():
            print("Flow or rainfall data contains NaN or infinite values.")
            return
    
        # Define synthetic flow generation function based on RTK parameters
        def generate_synthetic_flow(rainfall, R, T, K):
            synthetic_flow = np.zeros(len(rainfall))
            for i in range(len(rainfall)):
                for j in range(i):
                    if 0 <= i - j < T:
                        # Rising limb
                        synthetic_flow[i] += R * rainfall[j] * (i - j) / T
                    elif T <= i - j < T * (K + 1):
                        # Falling limb
                        synthetic_flow[i] += R * rainfall[j] * (T * (K + 1) - (i - j)) / (T * K)
            return synthetic_flow
    
        # Define the objective function for optimization with higher weighting for higher flow values
        def weighted_objective(params, rainfall, actual_flow):
            R1, T1, K1, R2, T2, K2 = params
            synthetic_flow1 = generate_synthetic_flow(rainfall, R1, T1, K1)
            synthetic_flow2 = generate_synthetic_flow(rainfall, R2, T2, K2)
            synthetic_flow = synthetic_flow1 + synthetic_flow2
            weights = actual_flow / np.max(actual_flow)  # Higher weights for higher flow values
            return mean_squared_error(actual_flow, synthetic_flow, sample_weight=weights)
    
        # Initial guess for RTK parameters
        initial_params = [1, 1, 1, 1, 2, 1]  # Ensure T2 > T1
        
        # Set bounds for the parameters to ensure they are positive
        bounds = [(0, None), (0, None), (0, None), (0, None), (0, None), (0, None)]
    
        # Optimize the RTK parameters to fit the data
        # Define a global variable to keep track of iterations
        iteration = 0

        def callback(xk):
            global iteration
            iteration += 1
            print(f'Iteration {iteration}: Current parameters: {xk}')

        result = minimize(weighted_objective, initial_params, args=(self.rainfall_values, self.flow_values), 
                        method='L-BFGS-B', bounds=bounds, callback=callback)
        
        # Check if optimization was successful
        if result.success:
            self.R1, self.T1, self.K1, self.R2, self.T2, self.K2 = result.x  # Store optimized RTK parameters as instance variables
            print(f"Optimized RTK Parameters Set 1: R1 = {self.R1:.2f}, T1 = {self.T1:.2f}, K1 = {self.K1:.2f}")
            print(f"Optimized RTK Parameters Set 2: R2 = {self.R2:.2f}, T2 = {self.T2:.2f}, K2 = {self.K2:.2f}")
        else:
            print("Optimization failed.")
            return
    
        # Generate synthetic flow using optimized RTK parameters over the entire range of df_rainfall
        full_rainfall_values = self.df_rainfall["Intensity(mm/hr)"].values
        synthetic_flow1 = generate_synthetic_flow(full_rainfall_values, self.R1, self.T1, self.K1)
        synthetic_flow2 = generate_synthetic_flow(full_rainfall_values, self.R2, self.T2, self.K2)
        full_synthetic_flow = synthetic_flow1 + synthetic_flow2
    
        # Store the synthetic flow in a DataFrame
        self.df_synthetic_flow = pd.DataFrame({
            "TimeGMT": self.df_rainfall["time_gmt_n"],
            "SyntheticFlow": full_synthetic_flow
        })
    
        # Store the training period for plotting purposes
        self.training_start_time = start_date
        self.training_end_time = end_date
    
        # Update the plot with the synthetic flow and training period
        self.plot_data()



    def get_rtk_parameters_and_synthetic_flow(self):
        return self.R1, self.T1, self.K1, self.R2, self.T2, self.K2, self.df_synthetic_flow
'''
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotWindow(root, "2024-10-01", "2024-10-20", df_raw_sump=df_sump_filtered, df_rainfall=df_rainfall_filtered, df_hour_agg_flow_meter=df_hour_agg_flow_meter_filtered, spill_level=95, sump_ylim=100)
    root.mainloop()
'''