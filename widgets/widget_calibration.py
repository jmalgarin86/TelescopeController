from PyQt5.QtWidgets import QGroupBox, QPushButton, QGridLayout, QHBoxLayout, QLabel, QComboBox, QVBoxLayout, \
    QSizePolicy, QRadioButton, QCheckBox


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
        self.button_dec = QPushButton("1) DEC")
        self.button_dec.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_p = QPushButton("2) AR  +")
        self.button_ar_p.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.button_ar_n = QPushButton("3) AR  -")
        self.button_ar_n.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # Create the checkboxes
        self.checkbox_dec = QCheckBox('', self)
        self.checkbox_dec.setEnabled(False)
        self.checkbox_ar_p = QCheckBox('', self)
        self.checkbox_ar_p.setEnabled(False)
        self.checkbox_ar_n = QCheckBox('', self)
        self.checkbox_ar_n.setEnabled(False)

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(self.button_dec, 0, 0)
        layout.addWidget(self.button_ar_p, 1, 0)
        layout.addWidget(self.button_ar_n, 2, 0)
        layout.addWidget(self.checkbox_dec, 0, 1)
        layout.addWidget(self.checkbox_ar_p, 1, 1)
        layout.addWidget(self.checkbox_ar_n, 2, 1)

        self.setLayout(layout)