# My PyQt App

This project is a PyQt application that replicates the functionality of a synthetic flow generation tool originally built using Streamlit. The application allows users to input rainfall data and parameters to generate synthetic flow and visualize the results.

## Project Structure

```
my-pyqt-app
├── src
│   ├── app.py          # Main application file for the PyQt app
│   ├── utils
│   │   └── synthetic_flow.py  # Contains the function to generate synthetic flow
├── requirements.txt    # Lists the dependencies required for the project
└── README.md           # Documentation for the project
```

## Requirements

To run this application, you need to install the following dependencies:

- PyQt5
- numpy
- matplotlib

You can install the required packages using pip. Make sure to create a virtual environment before installing the dependencies.

```bash
pip install -r requirements.txt
```

## Running the Application

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies as mentioned above.
4. Run the application using the following command:

```bash
python src/app.py
```

## Usage

- Enter rainfall intensity values at 30-minute intervals in the text area provided.
- Input the R, T, and K values for two sets.
- Specify the user-defined PFF.
- Click on "Generate Synthetic Flow" to see the results plotted and the required storage calculated.

## License

This project is licensed under the MIT License.