import numpy as np
import pyqtgraph as pg

from widgets.widget_plot import PlotWidget


class PlotController(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def updatePlot(self, x=None, y=None):
        # Set new data to the plots
        n = len(x)
        t = np.linspace(1, n, n)
        self.plot_x.setData(t, x)
        self.plot_y.setData(t, y)

        if self.text == 'pixel':
            values = np.concatenate((x, y), axis=0)

            # Calculate the slop of the regression line
            mean_t = np.mean(t)
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)
            m_y = np.sum((t - mean_t) * (y - mean_y)) / np.sum((t - mean_t) ** 2)

            # Update the info in the figure title
            self.setTitle('<font color="#FF0000">pixel: (%i, %i), slope: (%0.3f, %0.3f)</font>' %
                          (x[-1], y[-1], m_x, m_y))
        elif self.text == 'surface':
            values = x

            # Update the info in the figure title
            self.setTitle('<font color="#FF0000">surface: %0.1f</font>' % x[-1])

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(values) - 10, np.max(values) + 10])
