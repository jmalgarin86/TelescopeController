import sys

import cv2
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication

from widgets.widget_figure import FigureWidget


class GuideCameraController(FigureWidget):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = None
        self.square_position = None
        self.camera_guide = None
        self.square_position = (25, 25)
        self.square_size = (50, 50)
        self.timer = QTimer(self)

    def start_camera(self):
        if not self.camera_guide:
            self.camera_guide = cv2.VideoCapture(0)
            if self.camera_guide.isOpened():
                print("Camera 0 is ready!")
            else:
                print("Error: Could not open camera 0.")

            # # Set exposure time (value is in milliseconds)
            # exposure_time = -1  # Set your desired exposure time in milliseconds
            #
            # # Set exposure property (works for some cameras, not all)
            # self.camera_guide.set(cv2.CAP_PROP_EXPOSURE, exposure_time)

            # Create a timer to update the webcam feed
            self.timer.timeout.connect(self.update_frame)
        else:
            pass

        print("Start camera")

        # Start the timer
        self.timer.start(100)  # Update every 250 milliseconds (10 fps)

    def stop_camera(self):
        print("Stop camera")
        self.timer.stop()

    def update_frame(self):
        # Read a frame from the webcam
        ret, self.frame = self.camera_guide.read()

        # Check if the frame was read successfully
        if ret:
            # Draw a red square on the grayscale frame
            frame_with_square = self.draw_square(self.frame)

            # Convert the frame to RGB format
            rgb_image = cv2.cvtColor(frame_with_square, cv2.COLOR_BGR2RGB)

            # Convert the image to a format suitable for QLabel
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Add the image to the QGraphicsScene
            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(q_image))

            # Calculate the star centroid after each frame update
            if self.main.guiding_toolbar.action_tracking.isChecked():
                star_centroid, star_size = self.calculate_star_properties()
                if star_centroid:
                    self.square_position = star_centroid

    def draw_square(self, frame):
        # Create a copy of the frame to draw on
        frame_with_square = frame.copy()

        # Draw a red square on the frame at the stored position
        square_color = (255, 255, 255)  # Red color in BGR format
        center = self.square_position
        top_left = (center[0] - int(self.square_size[0]/2), center[1] - int(self.square_size[1]/2))
        bottom_right = (center[0] + int(self.square_size[0]/2), center[1] + int(self.square_size[1]/2))
        cv2.rectangle(frame_with_square, top_left, bottom_right, square_color, 2)

        return frame_with_square

    def mousePressEvent(self, event):
        # Capture the pixel position when the left mouse button is clicked
        if event.button() == Qt.LeftButton:
            # Get the position in image coordinates
            img_coords = self.view.mapToScene(event.pos())
            x, y = int(img_coords.x()), int(img_coords.y())

            # Check if the click is within the image area
            h, w, _ = self.camera_guide.read()[1].shape  # Get the actual image dimensions
            if 0 <= x < w and 0 <= y < h:
                self.square_position = (x, y)

        elif event.button() == Qt.RightButton:
            # Get the position in image coordinates
            img_coords = self.view.mapToScene(event.pos())
            x, y = int(img_coords.x()), int(img_coords.y())

            # Check if the click is within the image area
            h, w, _ = self.camera_guide.read()[1].shape  # Get the actual image dimensions
            if 0 <= x < w and 0 <= y < h:
                self.square_size = (int(np.abs(self.square_position[0]-x)*2), int(np.abs(self.square_position[1]-y)*2))

    def calculate_star_properties(self):
        # Check if square position and size are valid
        if self.square_position and self.square_size:
            # Get the center and half-size of the square
            center_x, center_y = self.square_position
            half_width, half_height = [int(size / 2) for size in self.square_size]

            # Calculate the top-left and bottom-right coordinates
            x = max(center_x - half_width, 0)
            y = max(center_y - half_height, 0)
            w = min(center_x + half_width, self.frame.shape[1]) - x
            h = min(center_y + half_height, self.frame.shape[0]) - y

            # Get the region of interest (ROI) within the square
            roi = self.frame[y:y+h, x:x+w]

            # Convert the ROI to grayscale
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Threshold the grayscale image to highlight the star pixels
            _, thresholded_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresholded_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if any contours were found
            if contours:
                # Find the contour with the maximum area (assuming it represents the star)
                max_contour = max(contours, key=cv2.contourArea)

                # Calculate the centroid of the star
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"]) + x
                    cy = int(M["m01"] / M["m00"]) + y

                    # Calculate the size of the star (bounding box area)
                    star_size = cv2.contourArea(max_contour)

                    return (cx, cy), star_size

        # Return None if square position or size is not valid
        return None, None

    def get_coordinates(self):
        return self.square_position

    def detect_and_select_star(self):
        # Check if the frame is available
        if self.frame is not None:
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # Threshold the grayscale frame to highlight stars
            _, thresholded_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Initialize variables to store information about the biggest star
            max_star_size = 0
            max_star_centroid = None

            # Iterate through detected contours
            for contour in contours:
                # Calculate the area of the contour
                star_size = cv2.contourArea(contour)

                # Update max_star_size and max_star_centroid if the current star is larger
                if star_size > max_star_size:
                    max_star_size = star_size

                    # Calculate the centroid of the star
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        max_star_centroid = (cx, cy)

            # Print information about the selected star
            if max_star_centroid is not None:
                print("Selected star centroid:", max_star_centroid)
                print("Selected star size:", max_star_size)

                # Set the square position to the centroid of the selected star
                self.square_position = max_star_centroid

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
        self.roi.setPos(self.x0 - roi_width / 2, self.y0 - roi_height / 2)
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

        self.surface = np.sum(binary_image) / 255

    def getCoordinates(self):
        return self.x0, self.y0, self.surface


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = GuideCameraController(main=True)
    main_window.show()
    main_window.start_camera()
    sys.exit(app.exec_())
