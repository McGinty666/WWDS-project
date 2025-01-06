from PyQt5 import QtWidgets, QtGui
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils.synthetic_flow import generate_synthetic_flow

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Synthetic Flow Generation")

        layout = QtWidgets.QVBoxLayout()

        self.rainfall_input = QtWidgets.QTextEdit(self)
        self.rainfall_input.setPlaceholderText("Enter rainfall intensity (mm/h) at 30-minute intervals, separated by commas:")
        layout.addWidget(self.rainfall_input)

        self.R1_input = QtWidgets.QDoubleSpinBox(self)
        self.R1_input.setValue(1.0)
        layout.addWidget(QtWidgets.QLabel("Enter R value for set 1:"))
        layout.addWidget(self.R1_input)

        self.T1_input = QtWidgets.QSpinBox(self)
        self.T1_input.setValue(1)
        layout.addWidget(QtWidgets.QLabel("Enter T value for set 1:"))
        layout.addWidget(self.T1_input)

        self.K1_input = QtWidgets.QDoubleSpinBox(self)
        self.K1_input.setValue(1)
        layout.addWidget(QtWidgets.QLabel("Enter K value for set 1:"))
        layout.addWidget(self.K1_input)

        self.R2_input = QtWidgets.QDoubleSpinBox(self)
        self.R2_input.setValue(1.0)
        layout.addWidget(QtWidgets.QLabel("Enter R value for set 2:"))
        layout.addWidget(self.R2_input)

        self.T2_input = QtWidgets.QSpinBox(self)
        self.T2_input.setValue(1)
        layout.addWidget(QtWidgets.QLabel("Enter T value for set 2:"))
        layout.addWidget(self.T2_input)

        self.K2_input = QtWidgets.QDoubleSpinBox(self)
        self.K2_input.setValue(1)
        layout.addWidget(QtWidgets.QLabel("Enter K value for set 2:"))
        layout.addWidget(self.K2_input)

        self.PFF_input = QtWidgets.QDoubleSpinBox(self)
        self.PFF_input.setValue(0.0)
        layout.addWidget(QtWidgets.QLabel("Enter the user-defined PFF:"))
        layout.addWidget(self.PFF_input)

        self.generate_button = QtWidgets.QPushButton("Generate Synthetic Flow", self)
        self.generate_button.clicked.connect(self.generate_synthetic_flow)
        layout.addWidget(self.generate_button)

        self.canvas = FigureCanvas(plt.Figure())
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def generate_synthetic_flow(self):
        rainfall = self.rainfall_input.toPlainText()
        rainfall = np.array([float(x) for x in rainfall.split(",")]) if rainfall else np.array([])

        R1 = self.R1_input.value()
        T1 = self.T1_input.value()
        K1 = self.K1_input.value()

        R2 = self.R2_input.value()
        T2 = self.T2_input.value()
        K2 = self.K2_input.value()

        PFF = self.PFF_input.value()

        synthetic_flow1 = generate_synthetic_flow(rainfall, R1, T1, K1)
        synthetic_flow2 = generate_synthetic_flow(rainfall, R2, T2, K2)
        overall_synthetic_flow = synthetic_flow1 + synthetic_flow2

        self.plot_results(overall_synthetic_flow, rainfall, PFF)

    def plot_results(self, overall_synthetic_flow, rainfall, PFF):
        self.canvas.figure.clear()
        ax1 = self.canvas.figure.add_subplot(111)

        ax1.plot(overall_synthetic_flow, label='Synthetic Flow', color='b')
        ax1.set_xlabel('Time (30-minute intervals)')
        ax1.set_ylabel('Synthetic Flow (m³/s)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()
        ax2.plot(rainfall, label='Rainfall', color='g')
        ax2.set_ylabel('Rainfall (mm/h)', color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        storage_required = np.trapz(overall_synthetic_flow) - PFF * len(overall_synthetic_flow)
        storage_required = max(storage_required, 0)

        ax1.legend()
        self.canvas.draw()

        QtWidgets.QMessageBox.information(self, "Storage Required", f"Storage required: {storage_required:.2f} m³")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())