import numpy as np
import pyqtgraph as pg

from widgets.widget_plot import PlotWidget


class PlotController(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def updatePlot(self, x):
        # Set new data to the plots
        n = len(x)
        t = np.linspace(1, n, n)
        self.plot.setData(t, x)

        # Calculate the slop of the regression line
        mean_t = np.mean(t)
        mean_x = np.mean(x)
        m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)

        # Update the info in the figure title
        self.setTitle('<font color="#FF0000">%s, pixel: %i, slope: %0.3f</font>' % (self.text, x[-1], m_x))

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(x) - 10, np.max(x) + 10])
