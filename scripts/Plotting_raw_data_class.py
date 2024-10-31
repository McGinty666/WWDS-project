import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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

        self.fig = Figure(figsize=(12, 6))
        self.ax1 = self.fig.add_subplot(111)
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

    def plot_data(self, initial=False):
        self.ax1.clear()

        # Use pre-filtered dataframes
        df_sump = self.df_sump_filtered
        df_rain = self.df_rainfall_filtered
        df_flow = self.df_flow_meter_filtered

        # Plot sump level
        if not df_sump.empty:
            self.ax1.plot(df_sump["TimeGMT"], df_sump["EValue"], color='green', label='Sump Level')
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Sump Level', color='green')
        self.ax1.tick_params(axis='y', labelcolor='green')

        # Spill level
        if self.spill_level:
            self.ax1.set_ylim(0, 1.2 * self.spill_level)
            self.ax1.axhline(y=self.spill_level, color='green', linestyle='--', label='Spill Level')

        # Plot rainfall if available with transparency and inverted axis
        if df_rain is not None and not df_rain.empty:
            ax2 = self.ax1.twinx()
            ax2.bar(df_rain["time_gmt_n"], df_rain["Intensity(mm/hr)"], color='blue', label='Rainfall', width=0.01, alpha=0.5)
            ax2.set_ylabel('Rainfall intensity (mm/h)', color='blue')
            ax2.tick_params(axis='y', labelcolor='blue')
            ax2.set_ylim(2, 0)  # Inverted axis

        # Plot flow meter data if available
        if df_flow is not None and not df_flow.empty:
            ax3 = self.ax1.twinx()
            ax3.spines['right'].set_position(('outward', 60))
            ax3.plot(df_flow["TimeGMT"], df_flow["meanEValue"], color='red', label='Mean EValue')
            ax3.set_ylabel('Mean EValue flow meter', color='red')
            ax3.tick_params(axis='y', labelcolor='red')
            ax3.set_ylim(0, 100) 

        self.ax1.set_xlim(self.start_time, self.end_time)
        self.ax1.set_title('Nearby Rainfall, Sump Level, and Mean EValue flow meter')
        self.ax1.grid(False)
        if df_rain is not None and not df_rain.empty:
            ax2.grid(False)
        if df_flow is not None and not df_flow.empty:
            ax3.grid(False)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotWindow(root, "2024-10-01", "2024-10-20", df_raw_sump=df_sump_filtered, df_rainfall=df_rainfall_filtered, df_hour_agg_flow_meter=df_hour_agg_flow_meter_filtered, spill_level=95, sump_ylim=100)
    root.mainloop()
