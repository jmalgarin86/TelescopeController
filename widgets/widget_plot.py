import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotWidget(QWidget):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)

        self.text = text  # Store the text for plot type

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

    def updatePlot(self, x=None, y=None):
        self.axes.clear()  # Clear the previous plot
        self.axes.set_facecolor('black')

        if x is None:
            return

        n = len(x)
        t = np.linspace(1, n, n)

        if self.text == 'pixel' and y is not None:
            self.axes.plot(t, x, label='x', color='red', marker='o')
            self.axes.plot(t, y, label='y', color='red', marker='x')
            values = np.concatenate((x, y), axis=0)
        elif self.text == 'surface':
            self.axes.plot(t, x, label='surface', color='red', marker='o')
            values = x
        else:
            return

        # Axes style again after clear
        self.axes.tick_params(colors='red')
        for spine in self.axes.spines.values():
            spine.set_color('red')
        self.axes.title.set_color('red')
        self.axes.xaxis.label.set_color('red')
        self.axes.yaxis.label.set_color('red')

        # Set limits
        self.axes.set_xlim(0, 100)
        self.axes.set_ylim(np.min(values) - 5, np.max(values) + 5)

        self.axes.legend(facecolor='black', edgecolor='red', labelcolor='red')
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = np.arange(0, 100, 1)
    y = np.arange(0, 200, 2)
    widget = PlotWidget(text='pixel')
    widget.updatePlot(x, y)
    widget.show()
    sys.exit(app.exec_())