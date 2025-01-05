import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils.synthetic_flow import generate_synthetic_flow

def main():
    st.title("Synthetic Flow Generation")

    # User inputs
    rainfall = st.text_area("Enter rainfall intensity (mm/h) at 30-minute intervals, separated by commas:")
    rainfall = np.array([float(x) for x in rainfall.split(",")]) if rainfall else np.array([])

    R1 = st.number_input("Enter R value for set 1:", value=1.0)
    T1 = st.number_input("Enter T value for set 1:", value=1)
    K1 = st.number_input("Enter K value for set 1:", value=1)

    R2 = st.number_input("Enter R value for set 2:", value=1.0)
    T2 = st.number_input("Enter T value for set 2:", value=1)
    K2 = st.number_input("Enter K value for set 2:", value=1)

    PFF = st.number_input("Enter the user-defined PFF:", value=0.0)

    if st.button("Generate Synthetic Flow"):
        synthetic_flow1 = generate_synthetic_flow(rainfall, R1, T1, K1)
        synthetic_flow2 = generate_synthetic_flow(rainfall, R2, T2, K2)
        overall_synthetic_flow = synthetic_flow1 + synthetic_flow2

        # Plotting
        fig, ax1 = plt.subplots()

        ax1.plot(overall_synthetic_flow, label='Synthetic Flow', color='b')
        ax1.set_xlabel('Time (30-minute intervals)')
        ax1.set_ylabel('Synthetic Flow (m³/s)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()
        ax2.plot(rainfall, label='Rainfall', color='g')
        ax2.set_ylabel('Rainfall (mm/h)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        st.pyplot(fig)

        # Storage calculation
        storage_required = np.trapz(overall_synthetic_flow) - PFF * len(overall_synthetic_flow)
        storage_required = max(storage_required, 0)

        st.write(f"Storage required: {storage_required:.2f} m³")

if __name__ == "__main__":
    main()