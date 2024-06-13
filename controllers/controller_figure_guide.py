import copy
import os
import sys
import time
import datetime

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
        self.frame_original = None
        self.astrophoto_mode = False
        self.n_frame = 0
        self.looseness_detected = "neutral"
        self.star_size_threshold = 8
        self.star_size = None
        self.dec_dir_old = None
        self.frame = None
        self.file_path = None
        self.tracking = False
        self.guiding = False
        self.reference_position = (0, 0)
        self.reference_position_prov = (0, 0)
        self.camera_guide = None
        self.square_position = (25, 25)
        self.square_size = (50, 50)
        self.timer = QTimer(self)
        self.x_vec = []
        self.y_vec = []
        self.s_vec = []

        # Create file to save data
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"log_{current_datetime}.txt"
        self.file = open(file_name, "w")

    @staticmethod
    def get_last_folder_in_directory(path):
        try:
            # List all directories in the given path
            directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
            if not directories:
                return None
            # Sort directories lexicographically and return the last one
            directories.sort()
            last_folder = directories[-1]
            return os.path.join(path, last_folder)
        except FileNotFoundError:
            return "Path not found"
        except PermissionError:
            return "Permission denied"
        except Exception as e:
            return str(e)

    @staticmethod
    def get_last_file_in_directory(path):
        try:
            # List all files in the given path
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            if not files:
                return None
            # Sort files lexicographically and return the last one
            files.sort()
            last_file = files[-1]
            return last_file
        except FileNotFoundError:
            return "Path not found"
        except PermissionError:
            return "Permission denied"
        except Exception as e:
            return str(e)

    def delete_all_except_last(self, path):
        last_file = self.get_last_file_in_directory(path)

        if last_file is None:
            # print("No files to delete.")
            return
        elif isinstance(last_file, str) and ("Path not found" in last_file or "Permission denied" in last_file):
            print(last_file)
            return

        try:
            # List all files in the given path
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

            # Delete all files except the last one
            for file in files:
                if file != last_file:
                    os.remove(os.path.join(path, file))
            # print("All files except the last one have been deleted.")
        except FileNotFoundError:
            print("Path not found")
        except PermissionError:
            print("Permission denied")
        except Exception as e:
            print(str(e))

    @staticmethod
    def extract_image_matrix(file_path):
        try:
            # Read the image using OpenCV
            img = cv2.imread(file_path, cv2.IMREAD_COLOR)
            if img is None:
                return "File not found or the image format is not supported"

            # Convert the image to a numpy array (matrix)
            image_matrix = np.array(img)
            return image_matrix
        except PermissionError:
            return "Permission denied"
        except Exception as e:
            return str(e)

    def start_camera(self):
        if not self.camera_guide:
            self.camera_guide = cv2.VideoCapture(1)
            if self.camera_guide.isOpened():
                print("Camera ready!")

                # Set exposure time (value is in milliseconds)
                exposure_time = -1  # Set your desired exposure time in milliseconds
                self.camera_guide.set(cv2.CAP_PROP_EXPOSURE, exposure_time)

                # Set the camera gain (adjust the value as needed)
                gain_value = 5000  # Set your desired gain value
                self.camera_guide.set(cv2.CAP_PROP_GAIN, gain_value)

                # Create a timer to update the webcam feed
                self.timer.timeout.connect(self.update_frame_from_camera)

                print("Start camera")

            else:   # Update frame from file
                print("Could not open camera. Checking for external files.")

                # Create timer to update the files
                self.timer.timeout.connect(self.update_frame_from_files)

            # Start the timer
            self.timer.start(100)  # Update every 100 milliseconds (10 fps)

        else:
            pass

    def stop_camera(self):
        print("Stop camera")
        self.timer.stop()

    def detect_and_select_star(self):
        # Check if the frame is available
        if self.frame is not None:
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # Threshold the grayscale frame to highlight stars
            _, thresholded_frame = cv2.threshold(gray_frame, 50, 255, cv2.THRESH_BINARY)

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

            # Set the square position to the centroid of the selected star
            if max_star_centroid is not None:
                self.square_position = max_star_centroid

    def update_frame_from_files(self):
        # Get file path
        path = self.get_last_folder_in_directory("/home/josalggui/AstroDMx_DATA")
        if path is None:
            file = None
        else:
            file = self.get_last_file_in_directory(path)
            self.delete_all_except_last(path)

        # Check if there is almost one file
        if file is None:
            file_path = self.file_path
        else:
            file_path = os.path.join(path, file)

        # Check for new frame
        if file_path != self.file_path:
            time.sleep(0.1)
            self.file_path = file_path
            self.frame_original = self.extract_image_matrix(file_path)
            self.n_frame += 1
        else:
            time.sleep(0.1)

        # Get frame
        self.frame = copy.copy(self.frame_original)

        # Get frame in gray scale
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # Resize the image to half its original size
        height, width = self.frame.shape[:2]
        self.frame = cv2.resize(self.frame, dsize=(width // 2, height // 2))

        # Multiply the image by a factor of 8, then clip to 0, 255
        if np.max(self.frame) > 0:
            self.frame = np.clip(self.frame * float(8), a_min=0, a_max=255).astype(np.uint8)

        # Calculate the star centroid and size after each frame update
        if self.tracking:
            # Get star centroid and size
            star_centroid, star_size = self.calculate_star_properties()

            # # Save info in the file
            self.file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} {star_centroid[0]} {star_centroid[1]} {star_size}\n")

            # Update plot and square position
            if star_centroid:
                self.square_position = star_centroid
                self.star_size = star_size

                # Ensure the length of the vectors is at most 100 elements
                if len(self.x_vec) == 100:
                    self.x_vec.pop(0)  # Remove the first element
                    self.y_vec.pop(0)
                    self.s_vec.pop(0)

                # Append new data to the list
                self.x_vec.append(star_centroid[0] - self.reference_position[0])
                self.y_vec.append(star_centroid[1] - self.reference_position[1])
                self.s_vec.append(star_size)

                # Update plots
                self.main.plot_controller_pixel.updatePlot(x=self.x_vec, y=self.y_vec)
                self.main.plot_controller_surface.updatePlot(x=self.s_vec)

        # Draw a red square on the grayscale frame
        frame_with_square = self.draw_square()

        # Convert the frame to RGB format
        rgb_image = cv2.cvtColor(frame_with_square, cv2.COLOR_BGR2RGB)

        # Convert the image to a format suitable for QLabel
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Add the image to the QGraphicsScene
        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(q_image))

    def update_frame_from_camera(self):
        # Read a frame from the webcam
        ret, self.frame = self.camera_guide.read()

        # Check if the frame was read successfully
        if ret:
            self.n_frame += 1

            # Get frame in gray scale
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # Resize the image to half its original size
            height, width = self.frame.shape[:2]
            self.frame = cv2.resize(self.frame, dsize=(width // 2, height // 2))

            # Multiply the image by a factor of 8, then clip to 0, 255
            if np.max(self.frame) > 0:
                self.frame = np.clip(self.frame * float(8), a_min=0, a_max=255).astype(np.uint8)

            # Calculate the star centroid and size after each frame update
            if self.tracking:
                # Get star centroid and size
                star_centroid, star_size = self.calculate_star_properties()

                # Save info in the file
                self.file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} {star_centroid[0]} {star_centroid[1]} {star_size}\n")

                # Update plot and square position
                if star_centroid:
                    self.square_position = star_centroid
                    self.star_size = star_size

                    # Ensure the length of the vectors is at most 100 elements
                    if len(self.x_vec) == 100:
                        self.x_vec.pop(0)  # Remove the first element
                        self.y_vec.pop(0)
                        self.s_vec.pop(0)

                    # Append new data to the list
                    self.x_vec.append(star_centroid[0] - self.reference_position[0])
                    self.y_vec.append(star_centroid[1] - self.reference_position[1])
                    self.s_vec.append(star_size)

                    # Update plots
                    self.main.plot_controller_pixel.updatePlot(x=self.x_vec, y=self.y_vec)
                    self.main.plot_controller_surface.updatePlot(x=self.s_vec)

            # Draw a red square on the grayscale frame
            frame_with_square = self.draw_square()

            # Convert the frame to RGB format
            rgb_image = cv2.cvtColor(frame_with_square, cv2.COLOR_BGR2RGB)

            # Convert the image to a format suitable for QLabel
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Add the image to the QGraphicsScene
            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(q_image))

    def do_guiding(self):

        # Get data from calibration
        vx_ra_p = self.main.calibration_controller.vx_ar_p
        vy_ra_p = self.main.calibration_controller.vy_ar_p
        vx_ra_n = self.main.calibration_controller.vx_ar_n
        vy_ra_n = self.main.calibration_controller.vy_ar_n

        # Get the initial list of folders in the directory
        items = os.listdir("sharpcap")
        initial_folders = [item for item in items if os.path.isdir(os.path.join("sharpcap", item))]
        n_files = 0
        new_folder = None
        self.reference_position_prov = self.get_reference_position()

        # Star guiding with updates in position after each frame
        current_frame = copy.copy(self.n_frame)
        while self.guiding:
            # Check if there is a new frame to avoid repetitions of movements
            if self.n_frame == current_frame:
                time.sleep(0.1)
                continue
            else:
                current_frame = copy.copy(self.n_frame)

            # Get reference position
            r0 = self.get_reference_position()
            x_star = r0[0]
            y_star = r0[1]

            # Get the updated list of folders in the directory
            items = os.listdir("sharpcap")
            current_folders = [item for item in items if os.path.isdir(os.path.join("sharpcap", item))]

            # Check for new folder
            if len(current_folders) > len(initial_folders):
                n_files = 0

                # Check for new folders
                new_folders = [folder for folder in current_folders if
                               folder not in initial_folders and os.path.isdir(os.path.join("sharpcap", folder))]
                new_folder = new_folders[0]

                # Reset initial_folders
                initial_folders = current_folders

            # Modify reference position in case new file is found
            if new_folder is None:
                pass
            else:
                time.sleep(0.1)
                folder_path = os.path.join("sharpcap", new_folder)
                folder_files = os.listdir(folder_path)
                if len(folder_files) > n_files:
                    n_files = len(folder_files)
                    dx = int(vx_ra_n * 2)
                    dy = int(vy_ra_n * 2)
                    x_star += dx
                    y_star += dy
                    self.set_reference_position((x_star, y_star))
                    print("Reference position: x, y: %0.0f, %0.0f" % (x_star, y_star))

            if self.get_star_size() > self.star_size_threshold:
                print("Missed alignment, guiding star lost...")
            else:
                # Align with actual reference position
                self.align_position(r0=(x_star, y_star))

            # Wait to next correction
            time.sleep(1)

    def go_to_reference(self):
        # Try to align with reference position and try again until it reach reference position
        while not self.check_position():
            self.align_position()

        return True

    def check_position(self):
        r0 = self.get_reference_position()
        r1 = self.get_coordinates()
        print("r0:")
        if r0 == r1:
            return True
        else:
            return False

    def align_position(self, r0=None):
        # Get reference position
        if r0 is None:
            r0 = self.reference_position

        # Get current position
        r1 = self.get_coordinates()

        # Calculate required displacement
        dr = np.array([r1[0] - r0[0], r1[1] - r0[1]])

        # Move the camera
        self.move_camera(dx=dr[0], dy=dr[1])

    def move_camera(self, dx=0, dy=0):
        # Set speed
        period = str(2)

        # Get data from calibration
        vx_de = self.main.calibration_controller.vx_de
        vy_de = self.main.calibration_controller.vy_de
        vx_ra_p = self.main.calibration_controller.vx_ar_p
        vy_ra_p = self.main.calibration_controller.vy_ar_p
        vx_ra_n = self.main.calibration_controller.vx_ar_n
        vy_ra_n = self.main.calibration_controller.vy_ar_n

        # Create matrix
        v_p = np.array([[vx_de, vx_ra_p], [vy_de, vy_ra_p]])
        v_n = np.array([[vx_de, vx_ra_n], [vy_de, vy_ra_n]])

        # Get required displacement
        dr = np.array([dx, dy])
        dr = -np.reshape(dr, (2, 1))

        # Get required steps
        n_steps = np.linalg.inv(v_p) @ dr
        if n_steps[1] < 0:
            n_steps = np.linalg.inv(v_n) @ dr
        n_steps[1] = n_steps[1]/2
        n_steps[0] = n_steps[0]*0.75    # To reduce the overshoot

        # Ensure Dec movement happens only in the required direction
        if (self.looseness_detected == "positive" and n_steps[0] < 0) or (self.looseness_detected == "negative" and n_steps[0] > 0):
            n_steps[0] = 0

        # Set directions
        if n_steps[0] >= 0 and self.main.manual_controller.dec_dir == 1:
            de_dir = str(1)
        elif n_steps[0] >= 0 and self.main.manual_controller.dec_dir == -1:
            de_dir = str(0)
        elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == 1:
            de_dir = str(0)
        elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == -1:
            de_dir = str(1)
        if n_steps[1] >= 0:
            ar_dir = str(1)
        else:
            ar_dir = str(0)

        # Limit the steps
        if n_steps[0] > 20:
            self.guiding = False
            print("\nStop guiding!")
        elif n_steps[0] < -20:
            self.guiding = False
            print("\nStop guiding!")
        if n_steps[1] > 20:
            self.guiding = False
            print("\nStop guiding!")
        if n_steps[1] < -20:
            self.guiding = False
            print("\nStop guiding!")
            
        # Get instructions
        de_steps = str(int(np.abs(n_steps[0])))
        ar_steps = str(int(np.abs(n_steps[1])))
        if de_steps == "0":
            de_command = " 0 0 0"
        else:
            de_command = " %s %s %s" % (de_steps, de_dir, period)
        if ar_steps == "0":
            ar_command = " 0 0 52"
        else:
            ar_command = " %s %s %s" % (ar_steps, ar_dir, period)

        # Send instructions
        if de_steps == "0" and ar_steps == "0":
            pass
        else:
            command = "0" + ar_command + de_command + "\n"
            self.main.waiting_commands.append(command)

            # Wait until it finish
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            while ser_input != "Ready!":
                ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
                time.sleep(0.01)

            print(command)

    def draw_square(self):
        # Create a copy of the frame to draw on
        frame_with_square = self.frame.copy()

        # Draw a white square on the frame at the stored position
        square_color = (255, 255, 255)  # White color in BGR format
        center = self.square_position
        top_left = (center[0] - int(self.square_size[0] / 2), center[1] - int(self.square_size[1] / 2))
        bottom_right = (center[0] + int(self.square_size[0] / 2), center[1] + int(self.square_size[1] / 2))
        cv2.rectangle(frame_with_square, top_left, bottom_right, square_color, 2)

        return frame_with_square

    def mousePressEvent(self, event):
        # Capture the pixel position when the left mouse button is clicked
        if event.button() == Qt.LeftButton:
            # Get the position in image coordinates
            img_coords = self.view.mapToScene(event.pos())
            x, y = int(img_coords.x()), int(img_coords.y())

            # Check if the click is within the image area
            h, w = self.frame.shape  # Get the actual image dimensions
            if 0 <= x < w and 0 <= y < h:
                self.square_position = (x, y)
                self.set_reference_position((x, y))
                print("Reference position: x, y: %0.1f, %0.1f" % (x, y))

        elif event.button() == Qt.RightButton:
            # Get the position in image coordinates
            img_coords = self.view.mapToScene(event.pos())
            x, y = int(img_coords.x()), int(img_coords.y())

            # Check if the click is within the image area
            h, w = self.frame.shape  # Get the actual image dimensions
            if 0 <= x < w and 0 <= y < h:
                self.square_size = (
                    int(np.abs(self.square_position[0] - x) * 2), int(np.abs(self.square_position[1] - y) * 2))

    def calculate_star_properties(self):
        # Check if square position and size are valid
        if self.square_position and self.square_size:
            # Get the center and half-size of the square
            center_x, center_y = self.square_position
            half_width, half_height = [int(size / 2) for size in self.square_size]

            # Calculate the top-left coordinates and size of square
            x = max(center_x - half_width, 0)
            y = max(center_y - half_height, 0)
            w = min(center_x + half_width, self.frame.shape[1]) - x
            h = min(center_y + half_height, self.frame.shape[0]) - y

            # Get the region of interest (ROI) within the square
            roi = self.frame[y:y + h, x:x + w]

            # Substract the background
            roi[roi <= np.max(roi)/2] = 0
            thresholded_roi = copy.copy(roi)
            thresholded_roi[roi > np.max(roi)/2] = 255

            # Show the thresholded image into the frame
            self.frame[y:y + h, x:x + w] = thresholded_roi

            # Get mass-center
            num_x = 0
            num_y = 0
            den = 0
            for ii in range(h):
                for jj in range(w):
                    num_y += roi[ii, jj] * ii
                    num_x += roi[ii, jj] * jj
                    den += roi[ii, jj]
            cx = num_x/den + x + 1
            cy = num_y/den + y + 1

            # Get standard deviation
            num = 0
            for ii in range(h):
                for jj in range(w):
                    num += roi[ii, jj] * np.sqrt((ii - cx + x + 1) ** 2 + (jj - cy + y + 1) ** 2)
                    den += roi[ii, jj]
            star_size = num/den

            return (int(cx), int(cy)), star_size
        else:
            return None, None

    def get_coordinates(self):
        return copy.copy(self.square_position)

    def get_star_size(self):
        return copy.copy(self.star_size)

    def set_reference_position(self, position: tuple):
        self.reference_position = copy.copy(position)

    def get_reference_position(self):
        return copy.copy(self.reference_position)

    def set_tracking(self, tracking: bool):
        self.tracking = tracking

    def set_guiding(self, guiding: bool):
        self.guiding = guiding

    def set_looseness(self, looseness):
        self.looseness_detected = looseness

    def set_star_threshold(self, threshold):
        self.star_size_threshold = threshold

    def set_astrophoto_mode(self, mode):
        self.astrophoto_mode = mode


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
