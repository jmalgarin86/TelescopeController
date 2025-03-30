import copy

from PyQt5.QtWidgets import QGroupBox, QPushButton, QGridLayout, QHBoxLayout, QLabel, \
    QSizePolicy, QRadioButton, QCheckBox, QSlider
from PyQt5.QtCore import Qt


class CalibrationWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Calibration")
        self.main = main

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        # Initially disabled
        # self.setEnabled(False)

        # Create QPushButtons
        self.button_dec_p = QPushButton("1) DEC +")
        self.button_dec_p.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_n = QPushButton("1) DEC -")
        self.button_dec_n.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_p = QPushButton("2) AR  +")
        self.button_ar_p.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_n = QPushButton("3) AR  -")
        self.button_ar_n.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_looseness = QPushButton("4) DEC looseness")
        self.button_dec_looseness.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_dec_looseness.setCheckable(True)
        self.button_load = QPushButton("Load")
        self.button_save = QPushButton("Save")

        # Create the checkboxes
        self.checkbox_dec_p = QCheckBox('', self)
        self.checkbox_dec_p.setEnabled(False)
        self.checkbox_dec_n = QCheckBox('', self)
        self.checkbox_dec_n.setEnabled(False)
        self.checkbox_ar_p = QCheckBox('', self)
        self.checkbox_ar_p.setEnabled(False)
        self.checkbox_ar_n = QCheckBox('', self)
        self.checkbox_ar_n.setEnabled(False)
        self.checkbox_dec_looseness = QCheckBox('', self)
        self.checkbox_dec_looseness.setEnabled(False)

        # Create strength sliders
        self.label_de = QLabel("DE strength: 1.0", self)
        self.slider_de = QSlider(Qt.Horizontal)
        self.slider_de.setMinimum(0)
        self.slider_de.setMaximum(10)
        self.slider_de.setValue(10)
        self.slider_de.setTickInterval(1)
        self.slider_de.setTickPosition(QSlider.TicksBelow)
        self.label_ar = QLabel("AR strength: 1.0", self)
        self.slider_ar = QSlider(Qt.Horizontal)
        self.slider_ar.setMinimum(0)
        self.slider_ar.setMaximum(10)
        self.slider_ar.setValue(10)
        self.slider_ar.setTickInterval(1)
        self.slider_ar.setTickPosition(QSlider.TicksBelow)

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(self.button_dec_p, 0, 0)
        layout.addWidget(self.button_dec_n, 1, 0)
        layout.addWidget(self.button_ar_p, 2, 0)
        layout.addWidget(self.button_ar_n, 3, 0)
        layout.addWidget(self.button_dec_looseness, 4, 0)
        layout.addWidget(self.checkbox_dec_p, 0, 1)
        layout.addWidget(self.checkbox_dec_n, 1, 1)
        layout.addWidget(self.checkbox_ar_p, 2, 1)
        layout.addWidget(self.checkbox_ar_n, 3, 1)
        layout.addWidget(self.checkbox_dec_looseness, 4, 1)

        # Layout for save/load buttons
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.button_load)
        layout_2.addWidget(self.button_save)
        layout.addLayout(layout_2, 7, 0, 1, 2)

        # Layout for de strength
        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.label_de)
        layout_3.addWidget(self.slider_de)
        layout.addLayout(layout_3, 5, 0, 1, 2)

        # Layout for ar strength
        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.label_ar)
        layout_4.addWidget(self.slider_ar)
        layout.addLayout(layout_4, 6, 0, 1, 2)

        self.setLayout(layout)
