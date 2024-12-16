import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QPushButton)
from PySide6.QtCore import QSize

class MatplotlibScatterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Fixed window size
        self.setFixedSize(QSize(1000, 600))
        self.setWindowTitle("Matplotlib Scatter Plot with PySide6")

        # Sample DataFrame
        number_rows = 20
        number_cols = 5
        self.df = pd.DataFrame(
            np.random.rand(number_rows,number_cols),
            columns=[f"Col{i+1}" for i in range(number_cols)]
        )
        self.df['Group'] = np.random.choice([f'G{x+1}' for x in range(3)],number_rows)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Plot Widget
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=3)

        # Controls Panel
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        layout.addWidget(controls_panel, stretch=1)

        # X-axis Selector
        controls_layout.addWidget(QLabel("Select X-Axis:"))
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItems(self.df.columns)
        controls_layout.addWidget(self.x_axis_combo)

        # Y-axis Selector
        controls_layout.addWidget(QLabel("Select Y-Axis:"))
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(self.df.columns)
        controls_layout.addWidget(self.y_axis_combo)

        # Color Selector
        controls_layout.addWidget(QLabel("Select Color Column:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.df.columns)
        controls_layout.addWidget(self.color_combo)

        # Buttons
        self.update_button = QPushButton("Update Plot")
        self.update_button.clicked.connect(self.update_plot)
        controls_layout.addWidget(self.update_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_plot)
        controls_layout.addWidget(self.reset_button)

        # Add stretch to the layout
        controls_layout.addStretch()

        # Initialize the plot
        self.update_plot()

    def update_plot(self):
        try:
            # Get selected columns
            x_col = self.x_axis_combo.currentText()
            y_col = self.y_axis_combo.currentText()
            color_col = self.color_combo.currentText()

            # Clear the previous plot
            self.ax.clear()

            # Map string values to colors
            color_mapping = {val: idx for idx, val in enumerate(self.df[color_col].unique())}
            colors = self.df[color_col].map(color_mapping)

            # Create scatter plot
            scatter = self.ax.scatter(self.df[x_col], self.df[y_col], c=colors, cmap="viridis")
            self.ax.set_title(f"Scatter Plot of {x_col} vs {y_col} Colored by {color_col}")
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)

            # Add grid and ticks
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.tick_params(axis='both', which='major', labelsize=10)

            # Add legend
            legend_labels = {idx: val for val, idx in color_mapping.items()}
            handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=scatter.cmap(scatter.norm(idx)), markersize=10)
                       for idx in legend_labels]
            self.ax.legend(handles, legend_labels.values(), title=color_col)

            # Refresh the canvas
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating plot: {e}")

    def reset_plot(self):
        self.x_axis_combo.setCurrentIndex(0)
        self.y_axis_combo.setCurrentIndex(1)
        self.color_combo.setCurrentIndex(2)
        self.update_plot()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatplotlibScatterApp()
    window.show()
    sys.exit(app.exec())
