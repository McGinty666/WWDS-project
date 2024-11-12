# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:55:31 2024

@author: RMCGINT
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class SpillAnalysis:
    def __init__(self, df_spill_hours):
        self.df_spill_hours = df_spill_hours

    def create_spill_duration_box_plot(self):
        # Extract year from spill_hours
        self.df_spill_hours['year'] = self.df_spill_hours['spill_hours'].dt.year

        # Group by year and spill_event_id and get the maximum spill_event_duration for each group
        max_durations = self.df_spill_hours.groupby(['year', 'spill_event_id'])['spill_event_duration'].max().reset_index()

        # Create a box plot for the distribution of the maximum spill_event_durations for each year
        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        sns.boxplot(x='year', y='spill_event_duration', data=max_durations)
        plt.title('Distribution of Spill Event Durations by Year')
        plt.xlabel('Year')
        plt.ylabel('Maximum Spill Event Duration (hours)')

        # Create an overall box plot for the distribution of the maximum spill_event_durations
        plt.subplot(1, 2, 2)
        sns.boxplot(y=max_durations['spill_event_duration'])
        plt.title('Overall Distribution of Spill Event Durations')
        plt.ylabel('Maximum Spill Event Duration (hours)')

        plt.gca().set_aspect(0.075)

        plt.tight_layout()
        plt.show()

    def calculate_total_spill_hours_per_month_year(self):
        # Extract year and month from spill_hours
        self.df_spill_hours['Year'] = self.df_spill_hours['spill_hours'].dt.year
        self.df_spill_hours['Month'] = self.df_spill_hours['spill_hours'].dt.month

        # Calculate total spill hours in each Month for each Year
        total_spill_hours_per_month_year = self.df_spill_hours.groupby(['Year', 'Month']).size().unstack(fill_value=0)

        # Create a bar chart of total spill hours in each Month with different colors for each Year
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot polygons for each Year with high transparency and add a line for each Year
        for year in total_spill_hours_per_month_year.index:
            ax.fill_between(total_spill_hours_per_month_year.columns, 0, total_spill_hours_per_month_year.loc[year], alpha=0.25, label=str(year))
            ax.plot(total_spill_hours_per_month_year.columns, total_spill_hours_per_month_year.loc[year], marker='o')

        # Set the x-axis labels to be the Months
        ax.set_xticks(total_spill_hours_per_month_year.columns)
        ax.set_xticklabels(total_spill_hours_per_month_year.columns)

        ax.set_xlabel('Month')
        ax.set_ylabel('Total Spill Hours')
        ax.set_title('Total Spill Hours in Each Month by Year')
        ax.legend(title='Year')
        plt.grid(True)
        plt.show()
