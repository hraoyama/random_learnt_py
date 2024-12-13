import sys
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QScrollBar, QLabel, QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go

class HeatmapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heatmap Viewer")
        self.setFixedSize(800, 600)  # Set fixed size for the window

        # Create sample DataFrame
        self.data = pd.DataFrame(
            np.random.rand(20, 10),
            columns=[f"Col {i}" for i in range(10)]
        )
        self.current_index = 0  # To track the current data view for the heatmap
        self.rows_to_display = 10

        # Main layout
        main_layout = QHBoxLayout()

        # Heatmap layout
        heatmap_layout = QVBoxLayout()

        # Plotly heatmap widget
        self.heatmap_view = QWebEngineView()
        self.update_heatmap()
        heatmap_layout.addWidget(self.heatmap_view)

        # Scrollbar widget
        scrollbar_widget = QWidget()
        scrollbar_layout = QVBoxLayout()
        scrollbar_layout.setContentsMargins(0, 0, 0, 0)

        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(999)  # Set scrollbar to have 1000 points
        self.scrollbar.setStyleSheet(
            """
            QScrollBar::handle:horizontal {
                height: 6px; 
                min-width: 10px; /* Minimum size of the handle */
                width: 50px;
            }
            """
        )
        self.scrollbar.valueChanged.connect(self.scroll_heatmap)

        scrollbar_layout.addWidget(self.scrollbar)
        scrollbar_widget.setLayout(scrollbar_layout)
        heatmap_layout.addWidget(scrollbar_widget)

        main_layout.addLayout(heatmap_layout)

        # Form and buttons layout
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Controls:"))

        btn1 = QPushButton("Button 1")
        btn2 = QPushButton("Button 2")
        btn3 = QPushButton("Button 3")

        form_layout.addRow(btn1)
        form_layout.addRow(btn2)
        form_layout.addRow(btn3)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def update_heatmap(self):
        """Update the heatmap based on the current data view."""
        displayed_data = self.data.iloc[
            self.current_index : self.current_index + self.rows_to_display
        ]

        fig = go.Figure(
            data=go.Heatmap(
                z=displayed_data.values,
                x=displayed_data.columns,
                y=displayed_data.index,
                colorscale=[[0, "red"], [0.5, "green"], [1, "blue"]],
            )
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            width=600,
            height=400,
        )

        # Render Plotly figure in QWebEngineView
        self.heatmap_view.setHtml(fig.to_html(include_plotlyjs="cdn"))

    def scroll_heatmap(self, value):
        """Handle scrolling to update the heatmap data."""
        self.current_index = int(value * (len(self.data) - self.rows_to_display) / 999)  # Map scrollbar value to data index
        self.update_heatmap()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatmapApp()
    window.show()
    sys.exit(app.exec())
