import threading
import time

import numpy as np

from widgets.widget_calibration import CalibrationWidget


class CalibrationController(CalibrationWidget):
    def __init__(self, main):
        super().__init__(main)

        # Connect buttons to actions
        self.vx_ar_n = None
        self.vy_ar_n = None
        self.vy_ar_p = None
        self.vx_ar_p = None
        self.vy_de = None
        self.vx_de = None
        self.button_dec.clicked.connect(self.calibrateDec)
        self.button_ar_p.clicked.connect(self.calibrateArP)
        self.button_ar_n.clicked.connect(self.calibrateArN)

    def calibrateDec(self):
        # Create a thread to do the calibration in parallel to the camera
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
        period = 26

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.guide_figure_controller.getCoordinates()

        # Set command to arduino
        if self.main.manual_controller.dec_dir == 1:
            command = "0 0 0 52 " + str(n_steps) + " 1 " + str(period) + "\n"
        else:
            command = "1 0 0 52 " + str(n_steps) + " 0 " + str(period) + "\n"
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        print(ser_input)

        # Get final coordinates
        x1, y1 = self.main.guide_figure_controller.getCoordinates()

        # Get characteristics
        self.vx_de = (x1 - x0) / n_steps
        self.vy_de = (y1 - y0) / n_steps

        print("vx_de: %0.5f" % self.vx_de)
        print("vy_de: %0.5f" % self.vy_de)

        # Show the check in the checkbox
        self.checkbox_dec.setChecked(True)

    def doCalibrateArP(self):
        print('Start AR + calibration')

        # Period is x0
        period = 26

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.guide_figure_controller.getCoordinates()

        # Set command to arduino
        command = "0 " + str(n_steps) + " 1 " + str(period) + " 0 0 0\n"
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        print(ser_input)

        # Get final coordinates
        x1, y1 = self.main.guide_figure_controller.getCoordinates()

        # Get characteristics
        self.vx_ar_p = (x1 - x0) / n_steps
        self.vy_ar_p = (y1 - y0) / n_steps

        print("vx_ar_p: %0.5f" % self.vx_ar_p)
        print("vy_ar_p: %0.5f" % self.vy_ar_p)

        # Show the check in the checkbox
        self.checkbox_ar_p.setChecked(True)

    def doCalibrateArN(self):
        print('Start AR - calibration')

        # Speed x2 in negative direction
        period = 26

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.guide_figure_controller.getCoordinates()

        # Set command to arduino
        command = "0 " + str(n_steps) + " 0 " + str(period) + " 0 0 0\n"
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        print(ser_input)

        # Get final coordinates
        x1, y1 = self.main.guide_figure_controller.getCoordinates()

        # Get characteristics
        self.vx_ar_n = - (x1 - x0) / n_steps
        self.vy_ar_n = - (y1 - y0) / n_steps

        print("vx_ar_n: %0.5f" % self.vx_ar_n)
        print("vy_ar_n: %0.5f" % self.vy_ar_n)

        # Show the check in the checkbox
        self.checkbox_ar_n.setChecked(True)
