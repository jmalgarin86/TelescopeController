import numpy as np
import pyqtgraph as pg

from widgets.widget_plot import PlotWidget


class PlotController(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def updatePlot(self, x, y):
        # Set new data to the plots
        n = len(x)
        t = np.linspace(1, n, n)
        self.plot_x.setData(t, x)
        self.plot_y.setData(t, y)

        # Calculate the slop of the regression line
        mean_t = np.mean(t)
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)
        m_y = np.sum((t - mean_t) * (y - mean_y)) / np.sum((t - mean_t) ** 2)

        # Update the info in the figure title
        self.setTitle('<font color="#FF0000">x, y, mx, my: %i, %i, %0.3f, %0.3f</font>' % (x[-1], y[-1], m_x, m_y))

        # Set axes range
        data = np.concatenate((np.array(x), np.array(y)), axis=0)
        self.setRange(xRange=[0, 100], yRange=[np.min(data) - 10, np.max(data) + 10])
