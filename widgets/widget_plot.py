import numpy as np
import pyqtgraph as pg


class PlotWidget(pg.PlotWidget):
    def __init__(self, main, text='None'):
        self.main = main
        self.text = text
        super().__init__()
        self.setFixedHeight(300)
