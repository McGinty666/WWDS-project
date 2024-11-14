# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:55:31 2024

@author: RMCGINT
"""


import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SpillAnalysis:
    def __init__(self, df_spill_hours):
        self.df_spill_hours = df_spill_hours

    def create_spill_duration_box_plot(self):
        self.df_spill_hours['year'] = self.df_spill_hours['spill_hours'].dt.year
        max_durations = self.df_spill_hours.groupby(['year', 'spill_event_id'])['spill_event_duration'].max().reset_index()

        fig, ax = plt.subplots(1, 2, figsize=(14, 6))
        sns.boxplot(x='year', y='spill_event_duration', data=max_durations, ax=ax[0])
        ax[0].set_title('Distribution of Spill Event Durations by Year')
        ax[0].set_xlabel('Year')
        ax[0].set_ylabel('Maximum Spill Event Duration (hours)')

        sns.boxplot(y=max_durations['spill_event_duration'], ax=ax[1])
        ax[1].set_title('Overall Distribution of Spill Event Durations')
        ax[1].set_ylabel('Maximum Spill Event Duration (hours)')

        fig.tight_layout()
        return fig

    def calculate_total_spill_hours_per_month_year(self):
        self.df_spill_hours['Year'] = self.df_spill_hours['spill_hours'].dt.year
        self.df_spill_hours['Month'] = self.df_spill_hours['spill_hours'].dt.month
        total_spill_hours_per_month_year = self.df_spill_hours.groupby(['Year', 'Month']).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        for year in total_spill_hours_per_month_year.index:
            ax.fill_between(total_spill_hours_per_month_year.columns, 0, total_spill_hours_per_month_year.loc[year], alpha=0.25, label=str(year))
            ax.plot(total_spill_hours_per_month_year.columns, total_spill_hours_per_month_year.loc[year], marker='o')

        ax.set_xticks(total_spill_hours_per_month_year.columns)
        ax.set_xticklabels(total_spill_hours_per_month_year.columns)
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Spill Hours')
        ax.set_title('Total Spill Hours in Each Month by Year')
        ax.legend(title='Year')
        plt.grid(True)
        
        return fig

def main():
    df_spill_hours = pd.DataFrame({
        'spill_hours': pd.date_range(start='1/1/2020', periods=100, freq='H'),
        'spill_event_id': [1]*50 + [2]*50,
        'spill_event_duration': [5]*50 + [10]*50
    })

    analysis = SpillAnalysis(df_spill_hours)

    root = tk.Tk()
    root.title("Spill Analysis")
    root.geometry("1200x600")

    frame_left = tk.Frame(root, bg='blue')
    frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    frame_right = tk.Frame(root)
    frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the DataFrame display
    text_frame = tk.Frame(frame_left)
    text_frame.pack(fill=tk.BOTH, expand=True)

    text_widget = scrolledtext.ScrolledText(text_frame, wrap='none', bg='blue', fg='white')
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scroll_y = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
    scroll_y.pack(side=tk.RIGHT, fill='y')

    scroll_x = tk.Scrollbar(text_frame, orient='horizontal', command=text_widget.xview)
    scroll_x.pack(side=tk.BOTTOM, fill='x')

    text_widget.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    text_widget.insert(tk.END, str(df_spill_hours))

    def display_plot(plot_func):
        for widget in frame_right.winfo_children():
            widget.destroy()
            
        fig = plot_func()
        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    btn1 = ttk.Button(frame_left, text="Spill Duration Box Plot", command=lambda: display_plot(analysis.create_spill_duration_box_plot))
    btn1.pack(pady=10)

    btn2 = ttk.Button(frame_left, text="Total Spill Hours per Month/Year", command=lambda: display_plot(analysis.calculate_total_spill_hours_per_month_year))
    btn2.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()


