import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from widgets.widget_figure import FigureWidget


class FigureController(FigureWidget):

    def __init__(self, *args):
        super().__init__(*args)
        self.roi_data = None
        self.roi_points = None

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
        self.roi_data = self.main.processing_toolbar.frames_grayscale[ind, x_min:x_max, y_min:y_max]
        self.roi_points = points

    def align_images(self):
        # Get frames
        frames = self.main.processing_toolbar.frames
        frames_grayscale = self.main.processing_toolbar.frames_grayscale
        x = []
        y = []

        # Match roi with frames to find the image displacement
        for frame_grayscale in frames_grayscale:
            result = cv2.matchTemplate(frame_grayscale, self.roi_data, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            x0, y0 = max_loc
            x.append(x0)
            y.append(y0)
        x = np.array(x)
        dx = x - x[0]
        y = np.array(y)
        dy = y - y[0]

        # Get the dimensions (width and height) of image2
        _, height, width = frames_grayscale.shape

        # Create an empty image of the same size as image2
        frames0_grayscale = np.zeros_like(frames_grayscale)
        frames0 = np.zeros_like(frames)

        # Align all the frames
        for ii in range(np.size(frames, 0)):
            # Calculate the new coordinates for image2 after shifting
            x1 = max(0, dx[ii])  # Ensure x1 is not negative
            x2 = min(width + dx[ii], width)  # Ensure x2 does not exceed the width
            y1 = max(0, dy[ii])  # Ensure y1 is not negative
            y2 = min(height + dy[ii], height)  # Ensure y2 does not exceed the height

            # Calculate the region in image1 where image2 will be placed
            x1_dst = max(0, -dx[ii])  # Destination coordinates
            x2_dst = min(width, width - dx[ii])
            y1_dst = max(0, -dy[ii])
            y2_dst = min(height, height - dy[ii])

            # Copy the shifted region from image2 to the corresponding region in shifted_image2
            frames0[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames[ii, y1:y2, x1:x2, :]
            frames0_grayscale[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames_grayscale[ii, y1:y2, x1:x2]

        frame1 = np.average(frames0, 0)
        frame1_grayscale = np.average(frames0_grayscale, 0)
        self.main.processing_toolbar.figure_rgb.setImage(frame1)
        self.main.processing_toolbar.figure_gray.setImage(frame1_grayscale)

        return 0
