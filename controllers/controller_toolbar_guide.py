import os
import threading
import time

import cv2
import numpy as np
from PyQt5.QtCore import QTimer

from widgets.widget_toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define parameters
        self.timer = None
        self.camera_main = None
        self.camera_guide = None
        self.y_star = 0
        self.x_star = 0
        self.x_vec = [0]
        self.y_vec = [0]
        self.s_vec = [0]
        self.tracking_enable = False

        # Connect buttons to actions
        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_camera.triggered.connect(self.start_camera)
        self.action_guide.triggered.connect(self.guiding)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_auto_star.triggered.connect(self.select_a_star)

    def select_a_star(self):
        self.main.guide_camera_controller.detect_and_select_star()

    def guiding(self):
        # Check if calibration is done
        check_de = self.main.calibration_controller.checkbox_dec.isChecked()
        check_ar_p = self.main.calibration_controller.checkbox_ar_p.isChecked()
        check_ar_n = self.main.calibration_controller.checkbox_ar_n.isChecked()
        if self.action_guide.isChecked():
            if check_de and check_ar_p and check_ar_n:
                print("Auto guide start")
                thread = threading.Thread(target=self.do_guiding)
                thread.start()
            else:
                print("No auto-guide")
        else:
            print("No auto-guide")

    def do_guiding(self):
        # Use current position as initial reference
        self.x_star, self.y_star = self.main.guide_camera_controller.get_coordinates()
        print("Reference position: x, y: %0.1f, %0.1f" % (self.x_star, self.y_star))

        # Check for speed
        period = str(10)

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

        # Get the initial list of files and folders in the directory
        initial_items = os.listdir("sharpcap")
        n_files = 0
        new_folder = None

        while self.action_guide.isChecked():
            # Get the updated list of files and folders in the directory
            current_items = os.listdir("sharpcap")

            # Check for new folder
            if len(current_items) > len(initial_items):
                n_files = 0

                # Check for new folders
                new_folders = [folder for folder in current_items if
                               folder not in initial_items and os.path.isdir(os.path.join("sharpcap", folder))]
                new_folder = new_folders[0]

                # Reset initial_files
                initial_items = current_items

            # Modify reference position in case new file is found
            if new_folder is None:
                pass
            else:
                folder_path = os.path.join("sharpcap", new_folder)
                folder_files = os.listdir(folder_path)
                if len(folder_files) > n_files:
                    n_files = len(folder_files)
                    dx = vx_ra_n * 2
                    dy = vy_ra_n * 2
                    self.x_star += dx
                    self.y_star += dy
                    print("Reference position: x, y: %0.1f, %0.1f" % (self.x_star, self.y_star))

            # Get required displacement
            x1, y1 = self.main.guide_camera_controller.get_coordinates()
            dr = np.array([x1 - self.x_star, y1 - self.y_star])
            dr = -np.reshape(dr, (2, 1))

            # Get required steps
            n_steps = np.linalg.inv(v_p) @ dr
            if n_steps[1] < 0:
                n_steps = np.linalg.inv(v_n) @ dr

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

            # Send instructions
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

            # Wait to next correction
            time.sleep(1)

    def start_camera(self):
        if self.action_camera.isChecked():
            # Open the camera 0 if it does not exist
            self.main.guide_camera_controller.start_camera()
        else:
            self.main.guide_camera_controller.stop_camera()

        return 0

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.main.arduino.serial_connection or not self.main.arduino.serial_connection.is_open:
                if self.main.arduino.connect():
                    self.action_arduino.setStatusTip("Disconnect Arduino")
                    self.action_arduino.setToolTip("Disconnect Arduino")
                    print("Arduino connected!")
                else:
                    self.action_arduino.setChecked(False)
        else:
            self.main.arduino.disconnect()
            self.action_arduino.setStatusTip("Connect Arduino")
            self.action_arduino.setToolTip("Connect Arduino")
            print("Arduino disconnected!")

    def tracking(self):
        if self.action_tracking.isChecked():
            print("Tracking Start")
        else:
            print("Tracking Stop")
