import csv
import threading
import time

import numpy as np

from widgets.widget_calibration import CalibrationWidget

class CalibrationController(CalibrationWidget):
    def __init__(self, main):
        super().__init__(main)

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
        self.button_calibration_test.clicked.connect(self.testCalibration)
        self.button_load.clicked.connect(self.load_calibration)
        self.button_save.clicked.connect(self.save_calibration)

    def testCalibration(self):
        # Create a thread to do the calibration test in parallel to the camera
        thread = threading.Thread(target=self.testCalibrationThread)
        thread.start()

    def testCalibrationThread(self):
        if self.button_calibration_test.isChecked():
            # Get initial coordinates
            self.x0, self.y0 = self.main.guide_camera_controller.get_coordinates()
            print("\nOrigin: %i, %i" % (self.x0, self.y0))

            # Move to desired target
            print("Target %i, %i" % (self.x0-50, self.y0-50))
            self.main.guide_camera_controller.align_position(r0=(self.x0-50, self.y0-50), period=str(10))
            time.sleep(5)
            self.x0, self.y0 = self.main.guide_camera_controller.get_coordinates()
            print("Got %i, %i" % (self.x0, self.y0))

            # Uncheck button
            self.button_calibration_test.setChecked(False)

    def calibrateDecLooseness(self):
        if self.button_dec_looseness.isChecked():
            # Get initial coordinates
            self.x0, self.y0 = self.main.guide_camera_controller.get_coordinates()
            self.checkbox_dec_looseness.setChecked(False)
        else:
            # Get final coordinates
            self.x1, self.y1 = self.main.guide_camera_controller.get_coordinates()

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
            dr = np.array([self.x1 - self.x0, self.y1 - self.y0])
            dr = -np.reshape(dr, (2, 1))

            # Get required steps
            n_steps = np.linalg.inv(v_p) @ dr
            if n_steps[1] < 0:
                n_steps = np.linalg.inv(v_n) @ dr

            # Get dec direction
            if n_steps[0] > 0:
                self.main.guide_camera_controller.set_looseness("positive")
                self.looseness_direction = "positive"
                print("Looseness positive")
            elif n_steps[0] < 0:
                self.main.guide_camera_controller.set_looseness("negative")
                self.looseness_direction = "negative"
                print("Looseness negative")
            elif n_steps[0] == 0:
                self.main.guide_camera_controller.set_looseness("neutral")
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
                self.vx_ar_n, self.vy_ar_n, self.vx_ar_p, self.vy_ar_p, self.vx_de, self.vy_de,self.looseness_direction = row
            self.vx_ar_n = float(self.vx_ar_n)
            self.vy_ar_n = float(self.vy_ar_n)
            self.vx_ar_p = float(self.vx_ar_p)
            self.vy_ar_p = float(self.vy_ar_p)
            self.vx_de = float(self.vx_de)
            self.vy_de = float(self.vy_de)
            self.main.guide_camera_controller.set_looseness(self.looseness_direction)

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
        print("\nCalibration loaded!")

    def save_calibration(self):
        # Check if calibration is done
        check_de = self.main.calibration_controller.checkbox_dec.isChecked()
        check_ar_p = self.main.calibration_controller.checkbox_ar_p.isChecked()
        check_ar_n = self.main.calibration_controller.checkbox_ar_n.isChecked()
        if check_de and check_ar_p and check_ar_n:
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
        period = 26

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.guide_camera_controller.get_coordinates()

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
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        print(ser_input)

        # Sleep 1 seconds to let the frame to refresh
        time.sleep(1)

        # Get final coordinates
        x1, y1 = self.main.guide_camera_controller.get_coordinates()

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
        x0, y0 = self.main.guide_camera_controller.get_coordinates()

        # Stop mount
        command = "1 0 0 0 0 0 0\n"
        self.main.waiting_commands.append(command)

        # Wit 5 seconds
        command = "0 0 0 52 0 0 0\n"
        time.sleep(5)
        self.main.waiting_commands.append(command)
        print("Ready!")

        # Sleep 1 seconds to let the frame refresh
        time.sleep(1)

        # Get final coordinates
        x1, y1 = self.main.guide_camera_controller.get_coordinates()

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
        period = 15

        # Number of steps (to be changed by an input)
        n_steps = 100

        # Get initial coordinates
        x0, y0 = self.main.guide_camera_controller.get_coordinates()

        # Set command to arduino
        command = "0 " + str(n_steps) + " 0 " + str(period) + " 0 0 0\n"
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        print(ser_input)

        # Sleep 1 seconds to let the frame to refresh
        time.sleep(1)

        # Get final coordinates
        x1, y1 = self.main.guide_camera_controller.get_coordinates()

        # Get characteristics
        self.vx_ar_n = - (x1 - x0) / n_steps
        self.vy_ar_n = - (y1 - y0) / n_steps

        print("vx_ar_n: %0.5f" % self.vx_ar_n)
        print("vy_ar_n: %0.5f" % self.vy_ar_n)

        # Show the check in the checkbox
        self.checkbox_ar_n.setChecked(True)

if __name__ == "__main__":
    main = 1
    controller = CalibrationController(main=main)
    controller.load_calibration()
