import sys

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QLineEdit, QSpinBox, QGridLayout, QWidget, QApplication

from controllers.controller_camera import MainCameraController, GuideCameraController
from controllers.controller_frames import FrameSniffer
from widgets.GroupBox import GroupBoxWithButtonTitle
import threading


class GuideCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Guide Camera")
        self.main = main

        # === Gain Input ===
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit("100")

        # === Exposure Input ===
        self.exposure_label = QLabel("Exposure (s):")
        self.exposure_input = QLineEdit("1")

        # === Connect Button ===
        self.connect_button = QPushButton("Connect Camera")
        self.connect_button.setCheckable(True)

        # === Update Button ===
        self.update_button = QPushButton("Update")
        self.update_button.setDisabled(True)

        # === Layout ===
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(self.connect_button, 0, 0, 1, 2)
        grid.addWidget(self.gain_label, 1, 0)
        grid.addWidget(self.gain_input, 1, 1)
        grid.addWidget(self.exposure_label, 2, 0)
        grid.addWidget(self.exposure_input, 2, 1)
        grid.addWidget(self.update_button, 3, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create guide camera controller
        self.guide_camera = GuideCameraController(main=self.main, device="ZWO CCD ASI120MC-S", timeout=5)
        self.guide_camera.signal_camera_ready.connect(self._camera_ready)

        # Connect buttons
        self.connect_button.clicked.connect(self.connect_camera)
        self.update_button.clicked.connect(self.update_camera)

        # Connect to guie camera
        self.connect_button.setChecked(True)
        self.connect_camera()


    def connect_camera(self):
        if self.connect_button.isChecked():
            if self.guide_camera.device_ccd is None:
                thread = threading.Thread(target=self._set_up_camera)
                thread.start()
            else:
                self._camera_ready()
        else:
            self.guide_camera.set_camera_status(status=False)
            self.update_button.setEnabled(False)
            print(f"Disconnected from {self.guide_camera.device}")

    def _camera_ready(self):
        self.guide_camera.set_camera_status(status=True)
        self.update_button.setEnabled(True)
        print(f"Connected to {self.guide_camera.device}")
    
    def _set_up_camera(self):
        self.guide_camera.set_up_camera()

    def update_camera(self):
        # Get gain
        try:
            gain = float(self.gain_input.text())
            self.guide_camera.set_gain(gain)
            print(f"Setting gain: {gain}")
        except ValueError:
            print("Invalid gain value")
            return

        # Get exposure
        try:
            exposure = float(self.exposure_input.text())
            self.guide_camera.set_exposure(exposure)
            print(f"Setting exposure: {exposure}")
        except ValueError:
            print("Invalid exposure value")
            return

class MainCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Main Camera")
        self.main = main
        self.captures_path = "captures"

        # === Number of Acquisitions ===
        self.num_acq_label = QLabel("Number of Acquisitions:")
        self.num_acq_input = QSpinBox()
        self.num_acq_input.setMinimum(1)
        self.num_acq_input.setMaximum(1000)
        self.num_acq_input.setValue(1)

        # === Capture Button ===
        self.capture_button = QPushButton("Capture Frames")
        self.capture_button.setCheckable(True)

        # === Layout ===
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(self.num_acq_label, 0, 0)
        grid.addWidget(self.num_acq_input, 0, 1)
        grid.addWidget(self.capture_button, 1, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create main camera controller
        self.main_camera = FrameSniffer(main=main, camera='main')

        # Connect update button to method
        self.capture_button.clicked.connect(self.capture_frames)

    def frames_ready(self):
        self.capture_button.setChecked(False)

    def capture_frames(self):
        if self.capture_button.isChecked():
            self.main_camera.set_frames_to_save(self.num_acq_input.value(), path='captures/')
        else:
            self.main_camera.set_frames_to_save(n=0, path='captures/')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.gui_open = True
    # widget = MainCameraWidget(main=main)
    widget = GuideCameraWidget(main=main)
    widget.show()
    sys.exit(app.exec_())