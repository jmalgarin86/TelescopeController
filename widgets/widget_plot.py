import numpy as np
import pyqtgraph as pg


class PlotWidget(pg.PlotWidget):
    def __init__(self, main, text='None'):
        self.main = main
        self.text = text
        super().__init__()
        self.setFixedHeight(300)

        # Set Initial configuration
        self.setLabel('bottom', 'Frame')
        self.setLabel('left', 'Pixel')

        # Generate some data points for the curves
        t = np.linspace(1, 100, 100)
        x = 20 + t * 0.1

        # Calculate the slop of the regression line
        mean_t = np.mean(t)
        mean_x = np.mean(x)
        m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)

        # Add the curves to the plot
        self.plot = self.plot(t, x, pen='g', symbol='o', symbolSize=8)

        # Create text items
        self.setTitle('<font color="#FF0000">%s, pixel: %i, slope: %0.3f</font>' % (self.text, x[-1], m_x))

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(x) - 10, np.max(x) + 10])