# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 15:53:46 2024

@author: RMCGINT
"""

from get_xy_fm_sl_from_siteid_v3 import get_rounded_coordinates, get_sump_analogue, get_flowmeter_signals

# Example usage
site_id = 15468 # Replace with the actual SITEID you want to search for

# Get rounded coordinates
rounded_x, rounded_y = get_rounded_coordinates(site_id)
if rounded_x is not None and rounded_y is not None:
    print(f"Rounded coordinates for SITEID {site_id}: X={rounded_x}, Y={rounded_y}")
else:
    print(f"SITEID {site_id} not found in the data.")

# Get sump analogue information
analogue_server, analogue_signal, spill_mm, pre_spill_mm = get_sump_analogue(site_id)
if analogue_server is not None and analogue_signal is not None:
    print(f"Sump level analogue info for SITEID {site_id}:")
    print(f"Analogue Server: {analogue_server}")
    print(f"Analogue Signal: {analogue_signal}")
    print(f"Spill(mm): {spill_mm}")
    print(f"Pre-Spill (mm): {pre_spill_mm}")
else:
    print(f"SITEID {site_id} not found in the asset register data.")

# Get flowmeter signal information
server, db_addr, db_name = get_flowmeter_signals(site_id)
if server is not None and db_addr is not None and db_name is not None:
    print(f"Flowmeter signal information for Site Id {site_id}:")
    print(f"Flowmeter Server: {server}")
    print(f"DB_ADDR: {db_addr}")
    print(f"DB_NAME: {db_name}")
else:
    print(f"Site Id {site_id} not found in the flowmeter signals data.")
