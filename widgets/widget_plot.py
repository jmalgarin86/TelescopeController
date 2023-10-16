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
        self.setLabel('left', 'Pixel Deviation')

        # Generate some data points for the curves
        t = np.linspace(1, 100, 100)
        x = t * 0

        # Calculate the slop of the regression line
        mean_t = np.mean(t)
        mean_x = np.mean(x)
        m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)

        # Add the curves to the plot
        self.addLegend()
        self.plot_x = self.plot(t, x, pen='r', symbol='o', symbolSize=8, name='x')
        self.plot_y = self.plot(t, x, pen='g', symbol='o', symbolSize=8, name='y')

        if self.text == 'pixel':
            values = np.concatenate((x, x), axis=0)

            # Update the info in the figure title
            self.setTitle('<font color="#FF0000">pixel: (%i, %i), slope: (%0.3f, %0.3f)</font>' %
                          (x[-1], x[-1], m_x, m_x))
        elif self.text == 'surface':
            values = x

            # Update the info in the figure title
            self.setTitle('<font color="#FF0000">surface: %0.1f</font>' % x[-1])

        # Set axes range
        self.setRange(xRange=[0, 100], yRange=[np.min(values) - 10, np.max(values) + 10])