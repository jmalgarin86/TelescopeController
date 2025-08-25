import csv
import os
import threading
import time

import numpy as np
from PyQt5.QtWidgets import QPushButton, QGridLayout, QHBoxLayout, QLabel, \
    QSizePolicy, QCheckBox, QSlider, QWidget
from PyQt5.QtCore import Qt

from widgets.GroupBox import GroupBoxWithButtonTitle


class CalibrationWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Calibration")
        self.main = main

        # Create QPushButtons
        self.button_dec_p = QPushButton("1) DEC +")
        self.button_dec_p.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_n = QPushButton("1) DEC -")
        self.button_dec_n.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_p = QPushButton("2) AR  +")
        self.button_ar_p.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_n = QPushButton("3) AR  -")
        self.button_ar_n.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_looseness = QPushButton("4) DEC looseness")
        self.button_dec_looseness.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_looseness.setCheckable(True)
        self.button_load = QPushButton("Load")
        self.button_save = QPushButton("Save")

        # Create the checkboxes
        self.checkbox_dec_p = QCheckBox('', self)
        self.checkbox_dec_p.setEnabled(False)
        self.checkbox_dec_n = QCheckBox('', self)
        self.checkbox_dec_n.setEnabled(False)
        self.checkbox_ar_p = QCheckBox('', self)
        self.checkbox_ar_p.setEnabled(False)
        self.checkbox_ar_n = QCheckBox('', self)
        self.checkbox_ar_n.setEnabled(False)
        self.checkbox_dec_looseness = QCheckBox('', self)
        self.checkbox_dec_looseness.setEnabled(False)

        # Create strength sliders
        self.label_de = QLabel("DE strength: 1.0", self)
        self.slider_de = QSlider(Qt.Horizontal)
        self.slider_de.setMinimum(0)
        self.slider_de.setMaximum(10)
        self.slider_de.setValue(10)
        self.slider_de.setTickInterval(1)
        self.slider_de.setTickPosition(QSlider.TicksBelow)
        self.label_ar = QLabel("AR strength: 1.0", self)
        self.slider_ar = QSlider(Qt.Horizontal)
        self.slider_ar.setMinimum(0)
        self.slider_ar.setMaximum(10)
        self.slider_ar.setValue(10)
        self.slider_ar.setTickInterval(1)
        self.slider_ar.setTickPosition(QSlider.TicksBelow)

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(self.button_dec_p, 0, 0)
        layout.addWidget(self.button_dec_n, 1, 0)
        layout.addWidget(self.button_ar_p, 2, 0)
        layout.addWidget(self.button_ar_n, 3, 0)
        layout.addWidget(self.button_dec_looseness, 4, 0)
        layout.addWidget(self.checkbox_dec_p, 0, 1)
        layout.addWidget(self.checkbox_dec_n, 1, 1)
        layout.addWidget(self.checkbox_ar_p, 2, 1)
        layout.addWidget(self.checkbox_ar_n, 3, 1)
        layout.addWidget(self.checkbox_dec_looseness, 4, 1)

        # Layout for save/load buttons
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.button_load)
        layout_2.addWidget(self.button_save)
        layout.addLayout(layout_2, 7, 0, 1, 2)

        # Layout for de strength
        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.label_de)
        layout_3.addWidget(self.slider_de)
        layout.addLayout(layout_3, 5, 0, 1, 2)

        # Layout for ar strength
        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.label_ar)
        layout_4.addWidget(self.slider_ar)
        layout.addLayout(layout_4, 6, 0, 1, 2)

        layout.setRowStretch(layout.rowCount(), 1)

        self.content.setLayout(layout)

        # Connect buttons to actions
        self.looseness_direction = None
        self.direction = +1
        self.vx_ar_n = None
        self.vy_ar_n = None
        self.vy_ar_p = None
        self.vx_ar_p = None
        self.vy_de = None
        self.vx_de = None
        self.x0 = None
        self.x1 = None
        self.y0 = None
        self.y1 = None
        self.button_dec_p.clicked.connect(self.calibrateDecP)
        self.button_dec_n.clicked.connect(self.calibrateDecN)
        self.button_ar_p.clicked.connect(self.calibrateArP)
        self.button_ar_n.clicked.connect(self.calibrateArN)
        self.button_dec_looseness.clicked.connect(self.calibrateDecLooseness)
        self.button_load.clicked.connect(self.load_calibration)
        self.button_save.clicked.connect(self.save_calibration)
        self.slider_de.valueChanged.connect(self.de_strength_changed)
        self.slider_ar.valueChanged.connect(self.ar_strength_changed)

    def de_strength_changed(self):
        strength = self.slider_de.value()
        self.label_de.setText(f"DE strength: {strength / 10}")
        self.main.image_guide_camera.set_strength(strength=strength, axis='dec')

    def ar_strength_changed(self):
        strength = self.slider_ar.value()
        self.label_ar.setText(f"AR strength: {strength / 10}")
        self.main.image_guide_camera.set_strength(strength=strength, axis='ar')

    def calibrateDecLooseness(self):
        if self.button_dec_looseness.isChecked():
            # Get initial coordinates
            self.x0, self.y0 = self.main.image_guide_camera.get_roi_position()
            self.checkbox_dec_looseness.setChecked(False)
        else:
            # Get final coordinates
            self.x1, self.y1 = self.main.image_guide_camera.get_roi_position()

            # Get data from calibration
            vx_de = self.vx_de
            vy_de = self.vy_de
            vx_ra_p = self.vx_ar_p
            vy_ra_p = self.vy_ar_p
            vx_ra_n = self.vx_ar_n
            vy_ra_n = self.vy_ar_n

            # Create matrix
            v_p = np.array([[vx_de, vx_ra_p], [vy_de, vy_ra_p]])
            v_n = np.array([[vx_de, vx_ra_n], [vy_de, vy_ra_n]])

            # Get required displacement
            dr = np.array([self.x1 - self.x0, self.y1 - self.y0])
            dr = -np.reshape(dr, (2, 1))

            # Get required steps
            n_steps = np.linalg.inv(v_p) @ dr
            if n_steps[1] < 0:
                n_steps = np.linalg.inv(v_n) @ dr

            # Get dec direction
            if n_steps[0] > 0:
                self.main.image_guide_camera.set_looseness("positive")
                self.looseness_direction = "positive"
                print("Looseness positive")
            elif n_steps[0] < 0:
                self.main.image_guide_camera.set_looseness("negative")
                self.looseness_direction = "negative"
                print("Looseness negative")
            elif n_steps[0] == 0:
                self.main.image_guide_camera.set_looseness("neutral")
                self.looseness_direction = "neutral"
                print("Looseness neutral")
            self.checkbox_dec_looseness.setChecked(True)

    def load_calibration(self):
        # Open the file in read mode
        with open("calibration/calibration.csv", mode='r') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)

            # Read the data
            for row in csv_reader:
                # Process each row of data
                self.vx_ar_n, self.vy_ar_n, self.vx_ar_p, self.vy_ar_p, self.vx_de, self.vy_de, self.looseness_direction = row
            self.vx_ar_n = float(self.vx_ar_n)
            self.vy_ar_n = float(self.vy_ar_n)
            self.vx_ar_p = float(self.vx_ar_p)
            self.vy_ar_p = float(self.vy_ar_p)
            self.vx_de = float(self.vx_de)
            self.vy_de = float(self.vy_de)
            self.main.image_guide_camera.set_looseness(self.looseness_direction)

        print("\nvx_ar_p: %0.5f px/s" % self.vx_ar_p)
        print("vy_ar_p: %0.5f px/s" % self.vy_ar_p)
        print("vx_ar_n: %0.5f px/step" % self.vx_ar_n)
        print("vx_ar_n: %0.5f px/step" % self.vy_ar_n)
        print("vx_de: %0.5f px/step" % self.vx_de)
        print("vy_de: %0.5f px/step" % self.vy_de)
        print("looseness direction: %s" % self.looseness_direction)

        self.checkbox_dec_p.setChecked(True)
        self.checkbox_dec_n.setChecked(True)
        self.checkbox_ar_n.setChecked(True)
        self.checkbox_ar_p.setChecked(True)
        self.checkbox_dec_looseness.setChecked(True)
        print("Calibration loaded!")

    def save_calibration(self):
        # Check if calibration is done
        check_de = self.checkbox_dec_p.isChecked()
        check_ar_p = self.checkbox_ar_p.isChecked()
        check_ar_n = self.checkbox_ar_n.isChecked()
        if check_de and check_ar_p and check_ar_n:
            if not os.path.exists('calibration'):
                os.mkdir('calibration')
            with open("calibration/calibration.csv", mode='w', newline='') as file:
                # Create a CSV writer object
                csv_writer = csv.writer(file)

                # Write the data
                csv_writer.writerow([self.vx_ar_n, self.vy_ar_n, self.vx_ar_p, self.vy_ar_p, self.vx_de, self.vy_de,
                                     self.looseness_direction])
            print("Calibration saved!")
        else:
            print("Calibrate first!")

    def calibrateDecP(self):
        # Create a thread to do the calibration in parallel to the camera
        self.direction = +1
        thread = threading.Thread(target=self.doCalibrateDec)
        thread.start()

    def calibrateDecN(self):
        # Create a thread to do the calibration in parallel to the camera
        self.direction = -1
        thread = threading.Thread(target=self.doCalibrateDec)
        thread.start()

    def calibrateArP(self):
        # Create a thread to do the calibration in parallel to the camera
        thread = threading.Thread(target=self.doCalibrateArP)
        thread.start()

    def calibrateArN(self):
        # Create a thread to do the calibration in parallel to the camera
        thread = threading.Thread(target=self.doCalibrateArN)
        thread.start()

    def doCalibrateDec(self):
        print('Start DEC calibration')

        # Check for speed x2
        period = 52

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.image_guide_camera.get_roi_position()

        # Set command to arduino
        if self.direction == +1:
            if self.main.manual_controller.dec_dir == 1:
                command = "0 0 0 52 " + str(n_steps) + " 1 " + str(period) + "\n"
            else:
                command = "0 0 0 52 " + str(n_steps) + " 0 " + str(period) + "\n"
        elif self.direction == -1:
            if self.main.manual_controller.dec_dir == 1:
                command = "0 0 0 52 " + str(n_steps) + " 0 " + str(period) + "\n"
            else:
                command = "0 0 0 52 " + str(n_steps) + " 1 " + str(period) + "\n"

        # Send command and wait to completion
        self._send_to_arduino(command)

        # Sleep 1 seconds to let the frame refresh
        time.sleep(5)
        print("Ready!")

        # Get final coordinates
        x1, y1 = self.main.image_guide_camera.get_roi_position()

        # Get characteristics
        self.vx_de = self.direction * (x1 - x0) / n_steps
        self.vy_de = self.direction * (y1 - y0) / n_steps

        print("vx_de: %0.5f" % self.vx_de)
        print("vy_de: %0.5f" % self.vy_de)

        # Show the check in the checkbox
        self.checkbox_dec_p.setChecked(True)
        self.checkbox_dec_n.setChecked(True)

    def doCalibrateArP(self):
        print('Start AR + calibration')

        # Get initial coordinates
        x0, y0 = self.main.image_guide_camera.get_roi_position()

        # Stop mount
        command = "1 0 0 0 0 0 0\n"
        self._send_to_arduino(command)

        # Wait 5 seconds
        command = "2 0 0 52 0 0 0\n"
        time.sleep(5)
        self._send_to_arduino(command)

        # Sleep 1 seconds to let the frame refresh
        time.sleep(5)
        print("Ready!")

        # Get final coordinates
        x1, y1 = self.main.image_guide_camera.get_roi_position()

        # Get characteristics
        self.vx_ar_p = (x1 - x0) / 5  # pixels per second
        self.vy_ar_p = (y1 - y0) / 5  # pixels per second

        print("vx_ar_p: %0.5f px/s" % self.vx_ar_p)
        print("vy_ar_p: %0.5f px/s" % self.vy_ar_p)

        # Show the check in the checkbox
        self.checkbox_ar_p.setChecked(True)

    def doCalibrateArN(self):
        print('Start AR - calibration')

        # Speed x2 in negative direction
        period = 26

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.image_guide_camera.get_roi_position()

        # Set command to arduino
        command = "0 " + str(n_steps) + " 0 " + str(period) + " 0 0 0\n"
        self._send_to_arduino(command)

        # Sleep 1 seconds to let the frame refresh
        time.sleep(5)
        print("Ready!")

        # Get final coordinates
        x1, y1 = self.main.image_guide_camera.get_roi_position()

        # Get characteristics
        self.vx_ar_n = - (x1 - x0) / n_steps
        self.vy_ar_n = - (y1 - y0) / n_steps

        print("vx_ar_n: %0.5f" % self.vx_ar_n)
        print("vy_ar_n: %0.5f" % self.vy_ar_n)

        # Show the check in the checkbox
        self.checkbox_ar_n.setChecked(True)

    def _send_to_arduino(self, command):
        self.main.arduino.waiting_response = True
        self.main.waiting_commands.append(command)
        while self.main.arduino.waiting_response:
            time.sleep(0.01)
