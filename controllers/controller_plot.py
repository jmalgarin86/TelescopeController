import numpy as np
import pyqtgraph as pg

from widgets.widget_plot import PlotWidget


class PlotController(PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set Initial configuration
        self.setLabel('bottom', 'Frame')

        # Generate some data points for the curves
        t = np.linspace(1, 100, 100)
        x = t * 0

        if self.text == 'pixel':
            # Add the curves to the plot
            self.addLegend()
            self.plot_x = self.plot(t, x, pen='r', symbol='o', symbolSize=8, name='x')
            self.plot_y = self.plot(t, x, pen='g', symbol='o', symbolSize=8, name='y')

            # Concatenate values
            values = np.concatenate((x, x), axis=0)
            # Update the info in the figure title
            self.setTitle('<font color="#FF0000">Star deviation</font>')
        elif self.text == 'surface':
            # Add the curves to the plot
            self.plot_x = self.plot(t, x, pen='r', symbol='o', symbolSize=8, name='x')
            # Update the info in the figure title
            values = x
            self.setTitle('<font color="#FF0000">Star surface</font>' % x[-1])

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(values) - 5, np.max(values) + 5])

    def updatePlot(self, x=None, y=None):
        # Set new data to the plots
        n = len(x)
        t = np.linspace(1, n, n)

        if self.text == 'pixel':
            self.plot_x.setData(t, x)
            self.plot_y.setData(t, y)
            values = np.concatenate((x, y), axis=0)
        elif self.text == 'surface':
            self.plot_x.setData(t, x)
            values = x

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(values) - 5, np.max(values) + 5])
