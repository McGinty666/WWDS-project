# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 11:25:47 2024

@author: RMCGINT
"""

import pandas as pd
import numpy as np


class SiteDataProcessor:
    def __init__(self, sites_list_path, asset_register_path, flowmeter_signals_path):
        self.df_sites_list = pd.read_excel(sites_list_path)
        self.df_asset_register = pd.read_excel(asset_register_path, header=1)
        self.df_flowmeter_signals = pd.read_excel(flowmeter_signals_path, sheet_name='Flowmeter Signals Nov22')
        
        # Strip any leading/trailing whitespace from column names
        self.df_sites_list.columns = self.df_sites_list.columns.str.strip()
        self.df_asset_register.columns = self.df_asset_register.columns.str.strip()
        self.df_flowmeter_signals.columns = self.df_flowmeter_signals.columns.str.strip()
        
        # Drop unnamed columns
        self.df_sites_list = self.df_sites_list.loc[:, ~self.df_sites_list.columns.str.contains('^Unnamed')]
    
    @staticmethod
    def round_to_nearest_500(num):
        rounded = round(num / 500) * 500
        if rounded % 1000 == 0:
            rounded += 500
        return rounded
    
    def get_rounded_coordinates(self, site_id):
        site_data = self.df_sites_list[self.df_sites_list['SITEID'] == site_id]
        if not site_data.empty:
            x_value = float(site_data['X'].values.item())
            y_value = float(site_data['Y'].values.item())
            rounded_x = self.round_to_nearest_500(x_value)
            rounded_y = self.round_to_nearest_500(y_value)
            return rounded_x, rounded_y
        else:
            return None, None
    
    def get_sump_analogue(self, site_id):
        asset_data = self.df_asset_register[self.df_asset_register['Site ID'] == site_id]
        if not asset_data.empty:
            analogue_server = asset_data['Analogue Server'].values.item()
            analogue_signal = asset_data['Analogue Signal'].values.item()
            spill_mm = asset_data['Spill (mm)'].values.item()
            pre_spill_mm = asset_data['Pre-Spill (mm)'].values.item()
            return analogue_server, analogue_signal, spill_mm, pre_spill_mm
        else:
            return None, None, None, None
    
    def get_flowmeter_signals(self, site_id):
        flowmeter_data = self.df_flowmeter_signals[self.df_flowmeter_signals['Site Id'] == site_id]
        if not flowmeter_data.empty:
            flowmeterserver = flowmeter_data['Server'].values
            db_addr_flow_meter = flowmeter_data['DB_ADDR'].values
            db_name_flow_meter = flowmeter_data['DB_NAME'].values
            return flowmeterserver, db_addr_flow_meter, db_name_flow_meter
        else:
            return None, None, None

# Example usage

if __name__ == "__main__":
    processor = SiteDataProcessor(
        '../ww_site_info/ww_sites_list.xlsx',
        '../ww_site_info/edm_asset_register.xlsx',
        '../ww_site_info/master_sps_flow_compliance.xlsx'
    )

    site_id = 19505

    rounded_x, rounded_y = processor.get_rounded_coordinates(site_id)
    if rounded_x is not None and rounded_y is not None:
        print(f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}")
    else:
        print(f"SITEID {site_id} not found in the data.")

    analogue_server, analogue_signal, spill_mm, pre_spill_mm = processor.get_sump_analogue(site_id)
    if analogue_server is not None and analogue_signal is not None:
        print(f"Sump level analogue info for SITEID {site_id}:")
        print(f"Analogue Server: {analogue_server}")
        print(f"Analogue Signal: {analogue_signal}")
        print(f"Spill(mm): {spill_mm}")
        print(f"Pre-Spill (mm): {pre_spill_mm}")
    else:
        print(f"SITEID {site_id} not found in the asset register data.")

    server, db_addr, db_name = processor.get_flowmeter_signals(site_id)
    if server is not None and db_addr is not None and db_name is not None:
        print(f"Flowmeter signal information for Site Id {site_id}:")
        print(f"Flowmeter Server: {server}")
        print(f"DB_ADDR: {db_addr}")
        print(f"DB_NAME: {db_name}")
    else:
        print(f"Site Id {site_id} not found in the flowmeter signals data.")
