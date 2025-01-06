
import numpy as np

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