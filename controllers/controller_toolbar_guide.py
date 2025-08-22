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

        # Connect buttons to actions
        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_guide.triggered.connect(self.guiding)

    def guiding(self):
        # Check if calibration is done
        check_de = self.main.calibration_widget.checkbox_dec_p.isChecked()
        check_ar_p = self.main.calibration_widget.checkbox_ar_p.isChecked()
        check_ar_n = self.main.calibration_widget.checkbox_ar_n.isChecked()
        if self.action_guide.isChecked():
            if check_de and check_ar_p and check_ar_n:
                position = self.main.image_guide_camera.get_roi_position()
                self.main.image_guide_camera.set_reference_position(position)
                self.main.image_guide_camera.set_guiding(True)
                self.main.image_guide_camera.dec_dir_old = None
                self.main.image_guide_camera.set_guiding(True)
                print("Start auto-guide")
                print("Reference position (x, y):", position)
            else:
                print("Calibrate first!")
                self.action_guide.setChecked(False)
        else:
            print("Stop auto-guide")
            self.main.image_guide_camera.set_guiding(False)

    def tracking(self):
        if self.action_tracking.isChecked():
            reference_position = self.main.image_guide_camera.get_roi_position()
            self.main.image_guide_camera.set_reference_position(reference_position)
            self.main.image_guide_camera.set_tracking(True)
            print(f"Reference position: {reference_position}")
            print("Start tracking")
        else:
            self.main.image_guide_camera.set_tracking(False)
            print("Stop tracking")

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

