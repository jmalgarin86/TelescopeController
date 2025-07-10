from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import sys
from PIL import Image


class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111, facecolor='black')

        # Axis style: red ticks and labels
        self.axes.tick_params(colors='red')
        for spine in self.axes.spines.values():
            spine.set_color('red')

        self.axes.title.set_color('red')
        self.axes.xaxis.label.set_color('red')
        self.axes.yaxis.label.set_color('red')

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def set_image(self, image_array):
        """Update the histogram based on a new image"""
        self.axes.clear()

        # Flatten grayscale or average color channels if needed
        if image_array.ndim == 2:
            data = image_array.ravel()
        else:  # RGB or RGBA
            data = image_array.mean(axis=2).ravel()

        self.axes.hist(data, bins=256, color='red', alpha=0.7)

        # Set ticks color
        self.axes.tick_params(colors='red')

        # Set spine (border) color
        for spine in self.axes.spines.values():
            spine.set_color('red')

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load initial image
    image_path = "../your_image.jpeg"
    image = Image.open(image_path)
    image_array = np.array(image)

    # Create and show widget
    window = HistogramWidget()
    window.set_image(image_array)
    window.show()
    sys.exit(app.exec_())