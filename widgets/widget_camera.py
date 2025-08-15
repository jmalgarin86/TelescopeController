import sys

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QLineEdit, QSpinBox, QGridLayout, QWidget, QApplication

from controllers.controller_camera import MainCameraController, GuideCameraController
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
        exposure = float(self.exposure_input.text())
        gain = float(self.gain_input.text())
        self.guide_camera.set_exposure(exposure=exposure)
        self.guide_camera.set_gain(gain=gain)

class MainCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Main Camera")
        self.main = main
        self.captures_path = "captures"

        # === Gain Input ===
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit("100")

        # === Exposure Input ===
        self.exposure_label = QLabel("Exposure (s):")
        self.exposure_input = QLineEdit("1")

        # === Temperature Input ===
        self.temp_label = QLabel("Temperature (°C):")
        self.temp_input = QLineEdit("0")

        # === Number of Acquisitions ===
        self.num_acq_label = QLabel("Number of Acquisitions:")
        self.num_acq_input = QSpinBox()
        self.num_acq_input.setMinimum(1)
        self.num_acq_input.setMaximum(1000)
        self.num_acq_input.setValue(1)

        # === Connect Button ===
        self.connect_button = QPushButton("Connect Camera")
        self.connect_button.setCheckable(True)

        # === Update Button ===
        self.update_button = QPushButton("Update")
        self.update_button.setDisabled(True)

        # === Capture Button ===
        self.capture_button = QPushButton("Capture Frames")
        self.capture_button.setCheckable(True)
        self.capture_button.setDisabled(True)

        # === Labels ===
        self.temperature_label = QLabel("Temperature:")
        self.power_label = QLabel("Power:")

        # === Layout ===
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(self.connect_button, 0, 0, 1, 2)
        grid.addWidget(self.gain_label, 1, 0)
        grid.addWidget(self.gain_input, 1, 1)
        grid.addWidget(self.exposure_label, 2, 0)
        grid.addWidget(self.exposure_input, 2, 1)
        grid.addWidget(self.temp_label, 3, 0)
        grid.addWidget(self.temp_input, 3, 1)
        grid.addWidget(self.num_acq_label, 4, 0)
        grid.addWidget(self.num_acq_input, 4, 1)
        grid.addWidget(self.update_button, 5, 0)
        grid.addWidget(self.capture_button, 5, 1)
        grid.addWidget(self.temperature_label, 6, 0)
        grid.addWidget(self.power_label, 6, 1)

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create main camera controller
        self.main_camera = MainCameraController(main=self.main, device="ZWO CCD ASI533MC Pro", timeout=5)
        self.main_camera.signal_frames_ready.connect(self.frames_ready)
        self.main_camera.signal_send_status.connect(self.monitor_status)
        self.main_camera.signal_camera_ready.connect(self._camera_ready)

        # Connect update button to method
        self.update_button.clicked.connect(self.update_camera_settings)
        self.connect_button.clicked.connect(self.connect_camera)
        self.capture_button.clicked.connect(self.capture_frames)

    def monitor_status(self, status):
        self.temperature_label.setText(f"Temperature: {status['Temperature']} ºC")
        self.power_label.setText(f"Power: {status['Power']} %")

    def connect_camera(self):
        if self.connect_button.isChecked():
            if self.main_camera.device_ccd is None:
                thread = threading.Thread(target=self._set_up_camera)
                thread.start()
            else:
                self._camera_ready()
        else:
            self.main_camera.set_camera_status(status=False)
            self.main_camera.set_cooling(cooling=False)
            self.update_button.setEnabled(False)
            self.capture_button.setEnabled(False)
            print(f"Disconnected from {self.main_camera.device}")
    
    def _camera_ready(self):
        self.main_camera.set_camera_status(status=True)
        self.update_button.setEnabled(True)
        self.capture_button.setEnabled(True)
        print(f"Connected to {self.main_camera.device}")
    
    def _set_up_camera(self):
        self.main_camera.set_up_camera()

    def update_camera_settings(self):
        # Get gain
        try:
            gain = float(self.gain_input.text())
            self.main_camera.set_gain(gain)
            print(f"Setting gain: {gain}")
        except ValueError:
            print("Invalid gain value")
            return

        # Get exposure
        try:
            exposure = float(self.exposure_input.text())
            self.main_camera.set_exposure(exposure)
            print(f"Setting exposure: {exposure}")
        except ValueError:
            print("Invalid exposure value")
            return

        # Get temperature
        temp_text = self.temp_input.text()
        try:
            temperature = float(temp_text)
            self.main_camera.set_temperature(temperature)
            print(f"Setting temperature: {temperature}")
        except ValueError:
            self.main_camera.set_cooling(False)
            print("Disabling temperature control")

    def frames_ready(self):
        self.capture_button.setChecked(False)

    def capture_frames(self):
        if self.capture_button.isChecked():
            self.main_camera.set_frames_to_save(self.num_acq_input.value(), path='captures/')
        else:
            self.main_camera.set_frames_to_save(frames_to_save=0, path='captures/')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.gui_open = True
    # widget = MainCameraWidget(main=main)
    widget = GuideCameraWidget(main=main)
    widget.show()
    sys.exit(app.exec_())