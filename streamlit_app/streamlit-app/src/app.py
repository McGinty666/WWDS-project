import streamlit as st
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from utils.synthetic_flow import generate_synthetic_flow

def main():
    st.title("Synthetic Flow, storage and pff simulator")

    # User inputs
    rainfall = st.text_area("Enter rainfall intensity (mm/h) at 5-minute intervals, separated by commas or spaces:")
    rainfall = np.array([float(x) for x in rainfall.replace(',', ' ').split()]) if rainfall else np.array([])

    # Ensure rainfall data length is a multiple of 12 by adding zeros if necessary
    if len(rainfall) % 12 != 0:
        padding_length = 12 - (len(rainfall) % 12)
        rainfall = np.pad(rainfall, (0, padding_length), 'constant')

    # Aggregate rainfall into hourly values by averaging each hour
    hourly_rainfall = np.mean(rainfall.reshape(-1, 12), axis=1)

    R1 = st.number_input("Enter R value for set 1:", value=4.4)
    T1 = st.number_input("Enter T value for set 1:", value=1)
    K1 = st.number_input("Enter K value for set 1:", value=16.43)

    R2 = st.number_input("Enter R value for set 2:", value=2.19)
    T2 = st.number_input("Enter T value for set 2:", value=9.5)
    K2 = st.number_input("Enter K value for set 2:", value=8)

    PFF = st.number_input("Enter the user-defined PFF (l/s):", value=0.0)

    if st.button("Generate Synthetic Flow"):
        synthetic_flow1 = generate_synthetic_flow(hourly_rainfall, R1, T1, K1)
        synthetic_flow2 = generate_synthetic_flow(hourly_rainfall, R2, T2, K2)
        overall_synthetic_flow = synthetic_flow1 + synthetic_flow2

        # Interpolate synthetic flow values for better granularity
        x = np.arange(len(overall_synthetic_flow))
        x_interp = np.linspace(0, len(overall_synthetic_flow) - 1, len(overall_synthetic_flow) * 10)
        interp_func = interp1d(x, overall_synthetic_flow, kind='cubic')
        overall_synthetic_flow_interp = interp_func(x_interp)

        # Plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        # Plot synthetic flows
        ax1.plot(x_interp, interp1d(x, synthetic_flow1, kind='cubic')(x_interp), label='Synthetic Flow 1', color='g')
        ax1.plot(x_interp, interp1d(x, synthetic_flow2, kind='cubic')(x_interp), label='Synthetic Flow 2', color='lime')
        ax1.plot(x_interp, overall_synthetic_flow_interp, label='Overall Synthetic Flow', color='black')
        ax1.axhline(y=PFF, color='r', linestyle='--', label='PFF')
        ax1.fill_between(x_interp, overall_synthetic_flow_interp, PFF, where=(overall_synthetic_flow_interp > PFF), color='orange', alpha=0.5)

        ax1.set_ylabel('Synthetic Flow (l/s)', color='g')
        ax1.tick_params(axis='y', labelcolor='g')
        ax1.legend(loc='upper left')

        # Plot rainfall
        ax2.bar(range(len(hourly_rainfall)), hourly_rainfall, label='Rainfall', color='b', alpha=0.6)
        ax2.set_ylabel('Rainfall (mm/h)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2.set_ylim(0, 120)  # Set max y-axis value to 120
        ax2.invert_yaxis()  # Invert y-axis for rainfall
        ax2.legend(loc='upper left')

        # Set x-axis ticks and labels for every 1 hour (12 intervals)
        x_ticks = np.arange(0, len(overall_synthetic_flow), 12)
        x_labels = [f'{i//12}h' for i in x_ticks]
        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(x_labels)

        ax1.set_xlabel('Time (hours)')

        st.pyplot(fig)

        # Storage calculation in cubic meters
        x_interp_seconds = x_interp * 3600  # Convert hourly intervals to seconds
        storage_required_liters = np.trapz(overall_synthetic_flow_interp[overall_synthetic_flow_interp > PFF] - PFF, x_interp_seconds[overall_synthetic_flow_interp > PFF])
        storage_required_m3 = storage_required_liters / 1000  # Convert liters to cubic meters
        storage_required_m3 = max(storage_required_m3, 0)

        st.write(f"Storage required: {storage_required_m3:.2f} m³")

if __name__ == "__main__":
    main()