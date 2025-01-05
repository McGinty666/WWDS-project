# Streamlit Synthetic Flow App

This project is a Streamlit application that allows users to input rainfall intensity and parameters to generate synthetic flow responses. The app visualizes the synthetic flow alongside the rainfall data and calculates the required storage based on user-defined parameters.

## Project Structure

```
streamlit-app
├── src
│   ├── app.py               # Main entry point of the Streamlit application
│   └── utils
│       └── synthetic_flow.py # Contains the synthetic flow generation function
├── requirements.txt         # Lists the dependencies required for the project
└── README.md                # Documentation for the project
```

## Installation

To run this application, you need to have Python installed on your machine. Follow these steps to set up the project:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To start the Streamlit application, run the following command in your terminal:

```
streamlit run src/app.py
```

Once the app is running, you can input the rainfall intensity in mm/h at 30-minute intervals, along with two sets of R, T, and K values. The app will generate the synthetic flow and display it alongside the rainfall data. You can also define a PFF line, and the app will calculate the storage required based on the area under the synthetic flow curve and the PFF line.

## Features

- Input rainfall intensity and RTK parameters.
- Generate synthetic flow based on user inputs.
- Visualize synthetic flow and rainfall on a dual-axis plot.
- Calculate and display required storage based on the PFF line.

## License

This project is licensed under the MIT License - see the LICENSE file for details.