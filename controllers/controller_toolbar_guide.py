import threading
import time

import cv2
import numpy as np

from widgets.widget_toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define parameters
        self.y_star = 0
        self.x_star = 0
        self.x_vec = []
        self.y_vec = []
        self.tracking_enable = False

        # Connect buttons to actions
        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_guide.triggered.connect(self.guiding)
        self.action_camera.triggered.connect(self.start_camera)
        self.action_select_position.triggered.connect(self.select_position)

    def select_position(self):
        self.x_star, self.y_star = self.main.figure_controller.getCoordinates()
        print("Reference position: x, y: %0.1f, %0.1f" % (self.x_star, self.y_star))

    def guiding(self):
        # Check if calibration is done
        check_de = self.main.calibration_controller.checkbox_dec.isChecked()
        check_ar_p = self.main.calibration_controller.checkbox_ar_p.isChecked()
        check_ar_n = self.main.calibration_controller.checkbox_ar_n.isChecked()
        if self.action_guide.isChecked():
            print("Guiding start")
            if check_de and check_ar_p and check_ar_n:
                thread = threading.Thread(target=self.do_guiding)
                thread.start()
            else:
                self.main.waiting_commands.append("0 0 0 52 0 0 0\n")
        else:
            print("Guide stop")
            self.main.waiting_commands.append("0 0 0 0 0 0 0\n")

    def do_guiding(self):
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

        while self.action_guide.isChecked():
            # Get required displacement
            x1, y1 = self.main.figure_controller.getCoordinates()
            dr = np.array([x1 - self.x_star, y1 - self.y_star])
            dr = np.reshape(dr, (2, 1))
            print("\nDeviation:")
            print(dr)

            # Get required steps
            n_steps = np.linalg.inv(v_p) @ dr
            if n_steps[1] < 0:
                n_steps = np.linalg.inv(v_n) @ dr
            print("Steps:")
            print(n_steps)

            # Set directions
            if n_steps[0] >= 0 and self.main.manual_controller.dec_dir == 1:
                de_dir = str(0)
            elif n_steps[0] >= 0 and self.main.manual_controller.dec_dir == -1:
                de_dir = str(1)
            elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == 1:
                de_dir = str(1)
            elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == -1:
                de_dir = str(0)
            if n_steps[1] >= 0:
                ar_dir = str(0)
                ar_per = period
            else:
                ar_dir = str(1)
                ar_per = period

            # Send instructions
            de_steps = str(int(np.abs(n_steps[0])))
            ar_steps = str(int(np.abs(n_steps[1])))
            if de_steps == "0":
                de_command = " 0 0 0"
                stop = str(1)
            else:
                stop = str(0)
                de_command = " %s %s %s" % (de_steps, de_dir, period)
            if ar_steps == "0":
                ar_command = " 0 0 52"
                stop = str(1)
            else:
                stop = str(0)
                ar_command = " %s %s %s" % (ar_steps, ar_dir, period)
            command = stop + ar_command + de_command
            print(command)
            self.main.waiting_commands.append(command)

            # Wait until it finish
            time1 = int(ar_steps) * int(period) * 2e-3
            time2 = int(de_steps) * int(period) * 2e-3
            # time.sleep(np.max(np.array([time1, time2])))
            # self.main.arduino.serial_connection.flushInput()
            while self.main.arduino.serial_connection.in_waiting == 0:
                time.sleep(0.01)
                pass
            self.main.arduino.serial_connection.flushInput()

            # Normal tracking
            # self.main.waiting_commands.append("0 0 0 52 0 0 0\n")

            # Wait to next correction
            time.sleep(0.1)

    def start_camera(self):
        # Create a VideoCapture object to access the camera.
        cap = cv2.VideoCapture(0)  # 0 for the default camera, you can specify a different camera index if needed.

        # Check if the camera was opened successfully.
        if not cap.isOpened():
            print("Error: Could not open camera.")
            exit()

        while True:
            # Read a frame from the camera.
            ret, frame = cap.read()

            if not ret:
                print("Error: Could not read a frame from the camera.")
                break

            # Get frame in grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the frame in a window.
            self.main.figure_controller.data = np.transpose(frame)
            self.main.figure_controller.setImage(np.transpose(frame))

            # If guide is activated
            if self.action_tracking.isChecked():
                # Get centroid of the star
                self.main.figure_controller.getCentroid()
                x0, y0 = self.main.figure_controller.getCoordinates()
                n = 100
                if len(self.x_vec) > n:
                    self.x_vec = self.x_vec[1::]
                    self.y_vec = self.y_vec[1::]
                self.x_vec.append(x0)
                self.y_vec.append(y0)
                self.main.plot_controller_x.updatePlot(self.x_vec)
                self.main.plot_controller_y.updatePlot(self.y_vec)

            # Check for the 'q' key to exit the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)

        # Release the camera and close the OpenCV window.
        cap.release()
        cv2.destroyAllWindows()

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.main.arduino.serial_connection or not self.main.arduino.serial_connection.is_open:
                if self.main.arduino.connect():
                    self.action_guide.setEnabled(True)
                    self.main.manual_controller.setEnabled(True)
                    self.main.auto_controller.setEnabled(True)
                    self.action_arduino.setStatusTip("Disconnect Arduino")
                    self.action_arduino.setToolTip("Disconnect Arduino")
                    print("Arduino connected!")
                else:
                    self.action_arduino.setChecked(False)
        else:
            self.main.arduino.disconnect()
            self.action_tracking.setEnabled(False)  # Disable the "Guiding" button
            self.main.manual_controller.setEnabled(False)
            self.main.auto_controller.setEnabled(False)
            self.action_arduino.setStatusTip("Connect Arduino")
            self.action_arduino.setToolTip("Connect Arduino")
            print("Arduino disconnected!")

    def tracking(self):
        if self.action_tracking.isChecked():
            print("Tracking Start")
        else:
            print("Tracking Stop")
