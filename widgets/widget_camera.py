import copy

from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QSizePolicy, QSlider, QVBoxLayout
from PyQt5.QtCore import Qt


class CameraWidget(QGroupBox):
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