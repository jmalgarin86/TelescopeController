import cv2
import numpy as np
import pyqtgraph as pg
from widgets.widget_figure import FigureWidget


class GuideFigureController(FigureWidget):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.surface = None
        self.x0 = None
        self.y0 = None
        self.x_ref = None
        self.y_ref = None

        self.data = data
        self.setImage(data, levels=(0, 255))

        # Hide menu button
        self.ui.menuBtn.hide()

        # Connect the mouse click signal to a custom slot
        self.getView().scene().sigMouseClicked.connect(self.mouseClickEvent)

        # Create line items for vertical and horizontal lines
        self.vertical_line = pg.InfiniteLine(pos=None, angle=90, movable=False, pen='g')
        self.horizontal_line = pg.InfiniteLine(pos=None, angle=0, movable=False, pen='g')
        self.vertical_line.hide()
        self.horizontal_line.hide()

        # Add lines to the ImageView
        self.getView().addItem(self.vertical_line)
        self.getView().addItem(self.horizontal_line)

    def setImage(self, data, levels=None):
        # Get the current histogram levels
        if levels is None:
            hist = self.getHistogramWidget()
            levels = hist.getLevels()

        # Set the image data
        super().setImage(data, levels=levels, autoHistogramRange=False)

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
            self.vertical_line.show()
            self.horizontal_line.show()
            self.ui.roiPlot.setMouseEnabled(True, True)
            self.ui.splitter.handle(1).setEnabled(True)  # Allow to change the window size
            self.roiChanged()
            for c in self.roiCurves:
                c.hide()
        else:
            self.roi.hide()
            try:
                self.vertical_line.show(False)
                self.horizontal_line.show(False)
            except:
                pass
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
        pass

    def mouseClickEvent(self, event):
        # Get the position of the mouse click in image coordinates
        pos = event.pos()
        img_coord = self.getImageItem().mapFromScene(pos)
        self.x0 = int(img_coord.x())
        self.y0 = int(img_coord.y())

        roi_width, roi_height = self.roi.size()
        self.roi.setPos(self.x0-roi_width/2, self.y0-roi_height/2)
        self.vertical_line.setPos(self.x0)
        self.horizontal_line.setPos(self.y0)

        # Get position of star in the roi
        self.getCentroid()
        self.x_ref = self.x0 * 1
        self.y_ref = self.y0 * 1

        # Show lines and roi
        self.ui.roiBtn.setChecked(True)
        self.roiClicked()

    def updateIndicator(self):
        self.vertical_line.setPos(self.x0)
        self.horizontal_line.setPos(self.y0)

    def getCentroid(self):
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

        points = points.astype(int)

        # Get roi in the grayscale
        x_min = np.min(points[0, :, :])
        y_min = np.min(points[1, :, :])

        # Star detection using thresholding within the ROI
        threshold = 140  # Adjust this threshold as needed
        _, binary_image = cv2.threshold(data, threshold, 255, cv2.THRESH_BINARY)

        # Ensure the binary_image is of data type CV_8U
        binary_image = np.uint8(binary_image)

        # Find connected components within the ROI
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)

        # Find the label of the largest connected component (assuming it's the star)
        if num_labels > 1:  # Ensure that there is at least one labeled component (the background)
            largest_component_label = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1

            # Get the center of the largest connected component (the star)
            self.y0, self.x0 = centroids[largest_component_label]

            # Transform the centroid coordinates to the coordinates of the full image
            self.x0 += x_min  # Add the x-coordinate of the ROI within the full image
            self.y0 += y_min  # Add the y-coordinate of the ROI within the full image

            # Calculate new top-left corner coordinates for the ROI
            roi_width, roi_height = data.shape[0], data.shape[1]
            x_min = int(self.x0 - roi_width / 2)
            y_min = int(self.y0 - roi_height / 2)

            self.roi.blockSignals(True)
            self.roi.setPos(x_min, y_min)
            self.vertical_line.setPos(self.x0)
            self.horizontal_line.setPos(self.y0)
            self.roi.blockSignals(False)

        self.surface = np.sum(binary_image)

    def getCoordinates(self):
        return self.x0, self.y0, self.surface
