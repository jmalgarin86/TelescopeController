import cv2
import numpy as np
import pyqtgraph as pg
from widgets.widget_figure import FigureWidget


class MainFigureController(FigureWidget):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x0 = None
        self.y0 = None
        self.x_ref = None
        self.y_ref = None

        self.data = data
        self.setImage(data, levels=(0, 255))

        # Hide buttons
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()

    def setImage(self, data, levels=None):
        # Get the current histogram levels
        if levels is None:
            hist = self.getHistogramWidget()
            levels = hist.getLevels()

        # Set the image data
        super().setImage(data, levels=levels, autoHistogramRange=False)
