import copy
import os
import sys

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QPushButton, QLineEdit, \
    QSpinBox, QGridLayout, QWidget, QApplication, QCheckBox
from PyQt5.QtCore import Qt

from controllers.controller_camera import MainCameraController
from widgets.GroupBox import GroupBoxWithButtonTitle


class GuideCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Guide Camera")
        self.main = main

        # Create sliders
        self.label_exp = QLabel("Exposure: 1.0 s", self)
        self.slider_exp = QSlider(Qt.Horizontal)
        self.slider_exp.setMinimum(0)
        self.slider_exp.setMaximum(100)
        self.slider_exp.setValue(50)
        self.slider_exp.setTickInterval(1)
        self.slider_exp.setTickPosition(QSlider.TicksBelow)
        self.label_gain = QLabel("Gain: 50", self)
        self.slider_gain = QSlider(Qt.Horizontal)
        self.slider_gain.setMinimum(0)
        self.slider_gain.setMaximum(100)
        self.slider_gain.setValue(50)
        self.slider_gain.setTickInterval(1)
        self.slider_gain.setTickPosition(QSlider.TicksBelow)

        # Main layout
        layout = QVBoxLayout()

        # Layout exposure
        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.label_exp)
        layout_1.addWidget(self.slider_exp)
        layout.addLayout(layout_1)

        # Layout for gain
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.label_gain)
        layout_2.addWidget(self.slider_gain)
        layout.addLayout(layout_2)
        layout.setStretch(1, 1)

        self.content.setLayout(layout)

        self.slider_exp.valueChanged.connect(self.set_exposure)
        self.slider_gain.valueChanged.connect(self.set_gain)

    def set_exposure(self):
        exposure = self.slider_exp.value()
        self.main.guide_camera_controller.exposure = exposure / 100 * 2
        self.label_exp.setText(f"Exposure: {exposure / 100 * 2} s")

    def set_gain(self):
        gain = self.slider_gain.value()
        self.main.guide_camera_controller.gain = gain / 100 * 5000
        self.label_gain.setText(f"Gain: {gain}")

class MainCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Main Camera")
        self.main = main
        self.captures_path = "Captures"

        # === Gain Input ===
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit("100")

        # === Exposure Input ===
        self.exposure_label = QLabel("Exposure (ms):")
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

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create main camera controller
        self.main_camera = MainCameraController(main=self.main, device="ZWO CCD ASI533MC Pro")
        self.main_camera.signal_frames_ready.connect(self.frames_ready)
        self.main_camera.signal_send_temperature.connect(self.temperature_monitor)

        # Connect update button to method
        self.update_button.clicked.connect(self.update_camera_settings)
        self.connect_button.clicked.connect(self.connect_camera)
        self.capture_button.clicked.connect(self.capture_frames)

    @staticmethod
    def temperature_monitor(temperature):
        print(f"Temperature: {temperature} ºC")

    def connect_camera(self):
        if self.connect_button.isChecked():
            if self.main_camera.device_ccd is None:
                self.main_camera.set_up_camera()
            self.main_camera.set_camera_status(status=True)
            self.update_button.setEnabled(True)
            self.capture_button.setEnabled(True)
            print(f"Connected to {self.main_camera.device}")
        else:
            self.main_camera.set_camera_status(status=False)
            self.main_camera.set_cooling(cooling=False)
            self.update_button.setEnabled(False)
            self.capture_button.setEnabled(False)
            print(f"Disconnected from {self.main_camera.device}")

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

        # Frames to capture
        self.main_camera.set_frames_to_save(self.num_acq_input.value())

    def frames_ready(self):
        self.capture_button.setChecked(False)

    def capture_frames(self):
        if self.capture_button.isChecked():
            self.main_camera.set_frames_to_save(self.num_acq_input.value())
        else:
            self.main_camera.set_frames_to_save(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.gui_open = True
    widget = MainCameraWidget(main=main)
    widget.show()
    sys.exit(app.exec_())