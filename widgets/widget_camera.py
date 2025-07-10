import copy
import sys

from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QSizePolicy, QSlider, QVBoxLayout, QPushButton, QLineEdit, \
    QSpinBox, QGridLayout, QWidget, QApplication, QCheckBox
from PyQt5.QtCore import Qt


class CameraGuideWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Camera control")
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

        self.setLayout(layout)

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

class CameraMainWidget(QGroupBox):
    def __init__(self, main=None):
        super().__init__()
        self.main = main

        # === Gain Input ===
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit()
        self.gain_input.setPlaceholderText("Enter gain value")

        # === Exposure Input ===
        self.exposure_label = QLabel("Exposure (ms):")
        self.exposure_input = QLineEdit()
        self.exposure_input.setPlaceholderText("Enter exposure in ms")

        # === Temperature Input ===
        self.temp_label = QLabel("Temperature (°C):")
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Enter target temperature")

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

        # === Capture Button ===
        self.capture_button = QPushButton("Capture Frames")

        # === Layout ===
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(self.gain_label, 0, 0)
        grid.addWidget(self.gain_input, 0, 1)

        grid.addWidget(self.exposure_label, 1, 0)
        grid.addWidget(self.exposure_input, 1, 1)

        grid.addWidget(self.temp_label, 2, 0)
        grid.addWidget(self.temp_input, 2, 1)

        grid.addWidget(self.init_temp_checkbox, 3, 1)

        grid.addWidget(self.filename_label, 4, 0)
        grid.addWidget(self.filename_input, 4, 1)

        grid.addWidget(self.num_acq_label, 5, 0)
        grid.addWidget(self.num_acq_input, 5, 1)

        layout.addLayout(grid)
        layout.addWidget(self.capture_button)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = CameraMainWidget(main=None)
    widget.show()
    sys.exit(app.exec_())