import time

import cv2
import numpy as np

from widgets.widget_toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tracking_enable = False

        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_guide.triggered.connect(self.guiding)
        self.action_camera.triggered.connect(self.start_camera)

    def guiding(self):
        if self.action_guide.isChecked():
            print("Guiding started")
        else:
            print("Guiding stoped")

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
            if self.action_guide.isChecked():
                # Get centroid of the star
                self.main.figure_controller.getCentroid()

                # # Update indicator
                # self.main.figure_controller.updateIndicator()

            # Check for the 'q' key to exit the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)

        # Release the camera and close the OpenCV window.
        cap.release()
        cv2.destroyAllWindows()

    def open_processing_gui(self):
        self.main.pro.showMaximized()

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.main.arduino.serial_connection or not self.main.arduino.serial_connection.is_open:
                if self.main.arduino.connect():
                    self.action_tracking.setEnabled(True)
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
            self.tracking_enable = True
            self.action_tracking.setText("Stop Guiding")
            self.main.waiting_commands.append("1 0 0 0 0 52\n")
            print("Tracking")
        else:
            self.tracking_enable = False
            self.action_tracking.setText("Start Guiding")
            self.main.waiting_commands.append("0 0 0 0 0 0\n")
            print("Stop")
