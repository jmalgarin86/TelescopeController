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
        self.action_camera.triggered.connect(self.start_camera)
        self.action_auto_star.triggered.connect(self.select_a_star)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_guide.triggered.connect(self.guiding)

    def select_a_star(self):
        self.main.guide_camera_controller.detect_and_select_star()

    def guiding(self):
        # Check if calibration is done
        check_de = self.main.calibration_controller.checkbox_dec.isChecked()
        check_ar_p = self.main.calibration_controller.checkbox_ar_p.isChecked()
        check_ar_n = self.main.calibration_controller.checkbox_ar_n.isChecked()
        if self.action_guide.isChecked():
            if check_de and check_ar_p and check_ar_n:
                position = self.main.guide_camera_controller.get_coordinates()
                self.main.guide_camera_controller.set_reference_position(position)
                self.main.guide_camera_controller.set_guiding(True)
                thread = threading.Thread(target=self.main.guide_camera_controller.do_guiding)
                thread.start()
                print("Start auto-guide")
                print("Reference position (x, y):", position)
            else:
                print("Calibrate first!")
                self.action_guide.setChecked(False)
        else:
            print("Stop auto-guide")
            self.main.guide_camera_controller.set_guiding(False)

    def tracking(self):
        if self.action_tracking.isChecked():
            self.main.guide_camera_controller.set_tracking(True)
            print("Start tracking")
        else:
            self.main.guide_camera_controller.set_tracking(False)
            print("Stop tracking")

    def start_camera(self):
        if self.action_camera.isChecked():
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

