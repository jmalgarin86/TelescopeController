import numpy as np
import pyqtgraph as pg


class PlotWidget(pg.PlotWidget):
    def __init__(self, main):
        self.main = main
        super().__init__()
        self.setFixedHeight(300)

        # Set Initial configuration
        self.setLabel('bottom', 'Frame')
        self.setLabel('left', 'Pixel')
        self.addLegend()

        # Generate some data points for the curves
        t = np.linspace(1, 100, 100)
        x = 20 + t * 0.1
        y = 30 + t * 0.12

        # Calculate the slop of the regression line
        mean_t = np.mean(t)
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        m_x = np.sum((t - mean_t) * (x - mean_x)) / np.sum((t - mean_t) ** 2)
        m_y = np.sum((t - mean_t) * (y - mean_y)) / np.sum((t - mean_t) ** 2)

        # Add the curves to the plot
        self.plot_x = self.plot(t, x, name='x', pen='g', symbol='o', symbolSize=8)
        self.plot_y = self.plot(t, y, name='y', pen='r', symbol='o', symbolSize=8)

        # Create text items
        last_x_position = x[-1]  # X position of the last data point
        last_y_position = y[-1]  # Y position of the last data point
        self.setTitle('<font color="#FF0000">x, y, mx, my: %i, %i, %0.3f, %0.3f</font>' % (last_x_position, last_y_position,
                                                                                     m_x, m_y))

        # Set axes range
        data = np.concatenate((np.array(x), np.array(y)), axis=0)
        self.setRange(xRange=[0, 100], yRange=[np.min(data) - 10, np.max(data) + 10])