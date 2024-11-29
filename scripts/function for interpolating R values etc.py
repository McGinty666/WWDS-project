import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Sample data
months = np.array([2, 6, 10])  # February, June, October
y_values = np.array([0.9531, 0.54891, 0.6482])

# Define the sine function to fit
def sine_function(x, a, b, c):
    return a * np.sin(2 * np.pi * x / 12 + b) + c

# Fit the sine function to the data
params, params_covariance = curve_fit(sine_function, months, y_values)

# Generate predictions for all months
all_months = np.arange(1, 13)
predicted_values = sine_function(all_months, *params)

# Plot the results
plt.figure(figsize=(10, 6))
plt.scatter(months, y_values, color='red', label='Sample Data')
plt.plot(all_months, predicted_values, label='Fitted Sine Wave', color='blue')
plt.xlabel('Month')
plt.ylabel('Value')
plt.title('Fitting Sine Wave to Sample Data')
plt.legend()
plt.xticks(all_months)
plt.grid(True)
plt.show()

# Print the fitted parameters and predicted values
print("Fitted parameters (a, b, c):", params)
print("Predicted values for each month:", predicted_values)