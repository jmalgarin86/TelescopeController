import copy
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

        # === Gain Input ===
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit("100")

        # === Exposure Input ===
        self.exposure_label = QLabel("Exposure (ms):")
        self.exposure_input = QLineEdit("1")

        # === Temperature Input ===
        self.temp_label = QLabel("Temperature (°C):")
        self.temp_input = QLineEdit("0")

        # === Initialize Temperature Checkbox ===
        self.init_temp_checkbox = QCheckBox("Initialize Temperature")

        # === File Name Input ===
        self.filename_label = QLabel("Save File Name:")
        self.filename_input = QLineEdit()

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

        # === Capture Button ===
        self.capture_button = QPushButton("Capture Frames")
        self.capture_button.setCheckable(True)

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

        grid.addWidget(self.filename_label, 4, 0)
        grid.addWidget(self.filename_input, 4, 1)

        grid.addWidget(self.num_acq_label, 5, 0)
        grid.addWidget(self.num_acq_input, 5, 1)

        grid.addWidget(self.update_button, 6, 0)
        grid.addWidget(self.capture_button, 6, 1)

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create main camera controller
        self.main_camera = MainCameraController(main=self.main, device="ZWO CCD ASI533MC Pro")

        # Connect update button to method
        self.update_button.clicked.connect(self.update_camera_settings)
        self.connect_button.clicked.connect(self.connect_camera)

        self.show()

    def connect_camera(self):
        if self.connect_button.isChecked():
            if self.main_camera.device_ccd is None:
                self.main_camera.set_up_camera()
            self.main_camera.set_camera_status(status=True)
            print(f"Connected to {self.main_camera.device}")
        else:
            self.main_camera.set_camera_status(status=False)
            print(f"Disconnected from {self.main_camera.device}")

    def update_camera_settings(self):
        # Get gain
        try:
            gain = float(self.gain_input.text())
        except ValueError:
            print("Invalid gain value")
            return

        # Get exposure
        try:
            exposure = float(self.exposure_input.text())
        except ValueError:
            print("Invalid exposure value")
            return

        # Get temperature
        temp_text = self.temp_input.text()
        if temp_text.strip().lower() == "off":
            temperature = None  # means disable cooling
        else:
            try:
                temperature = float(temp_text)
            except ValueError:
                print("Invalid temperature value")
                return

        # === Call your camera methods ===
        print(f"Setting gain: {gain}")
        print(f"Setting exposure: {exposure}")
        if temperature is None:
            print("Disabling temperature control")
        else:
            print(f"Setting temperature: {temperature}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.gui_open = True
    widget = MainCameraWidget(main=main)
    sys.exit(app.exec_())