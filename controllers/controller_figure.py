import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from widgets.widget_figure import FigureWidget


class FigureController(FigureWidget):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setImage(data)

    def roiClicked(self):
        """
        Handle the event when the ROI button is clicked.

        This method shows or hides the ROI plot based on the button state. It also updates the visibility of the ROI
        and the time line.

        """
        show_roi_plot = False
        if self.ui.roiBtn.isChecked():
            show_roi_plot = True
            self.roi.show()
            self.ui.roiPlot.setMouseEnabled(True, True)
            self.ui.splitter.handle(1).setEnabled(True)  # Allow to change the window size
            self.roiChanged()
            for c in self.roiCurves:
                c.hide()
        else:
            self.roi.hide()
            self.ui.roiPlot.setMouseEnabled(False, False)
            for c in self.roiCurves:
                c.hide()
            self.ui.roiPlot.hideAxis('left')

        if self.hasTimeAxis():
            show_roi_plot = True
            mn = self.tVals.min()
            mx = self.tVals.max()
            self.ui.roiPlot.setXRange(mn, mx, padding=0.01)
            self.timeLine.show()
            self.timeLine.setBounds([mn, mx])
            if not self.ui.roiBtn.isChecked():
                self.ui.splitter.handle(1).setEnabled(False)
        else:
            self.timeLine.hide()

        self.ui.roiPlot.setVisible(show_roi_plot)

    def roiChanged(self):
        """
        Update the plot and text items based on the selected region of interest (ROI).

        This method extracts the image data within the ROI, calculates necessary statistics, and updates the plot and
        text items accordingly.

        """
        # Extract image data from ROI
        if self.image is None:
            return

        image = self.getProcessedImage()

        # getArrayRegion axes should be (x, y) of data array for col-major,
        # (y, x) for row-major
        # can't just transpose input because ROI is axisOrder aware
        colmaj = self.imageItem.axisOrder == 'col-major'
        if colmaj:
            axes = (self.axes['x'], self.axes['y'])
        else:
            axes = (self.axes['y'], self.axes['x'])

        # Get the coordinates of the roi
        data, points = self.roi.getArrayRegion(
            image.view(np.ndarray), img=self.imageItem, axes=axes,
            returnMappedCoords=True)
        if points is None:
            return

        # Get slice
        (ind, time) = self.timeIndex(self.timeLine)

        points = points.astype(int)

        # Get roi in the grayscale
        x_min = np.min(points[0, :, :])
        x_max = np.max(points[0, :, :])+1
        y_min = np.min(points[1, :, :])
        y_max = np.max(points[1, :, :])+1
        self.main.roi_data = self.main.processing_toolbar.frames_grayscale[ind, x_min:x_max, y_min:y_max]
        self.main.roi_points = points
