from PyQt5.QtWidgets import QGroupBox, QPushButton, QGridLayout, QHBoxLayout, QLabel, QComboBox, QVBoxLayout, \
    QSizePolicy, QRadioButton


class ManualWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Manual Control")
        self.main = main

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        # Initially disabled
        # self.setEnabled(False)

        # Create QPushButtons
        self.button_ar_p = QPushButton("AR  +")
        self.button_ar_n = QPushButton("AR  -")
        self.button_dec_p = QPushButton("DEC +")
        self.button_dec_n = QPushButton("DEC -")
        self.button_ar_p.setCheckable(True)
        self.button_ar_n.setCheckable(True)
        self.button_dec_p.setCheckable(True)
        self.button_dec_n.setCheckable(True)

        # Create a label for the speed selection
        speed_label = QLabel("Speed")

        # Create a QComboBox for speed selection
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["x0.5", "x1", "x2", "x4", "x13", "x26"])

        # Set the horizontal size policy for speed_label and speed_combo
        speed_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.speed_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Create QComboBox layout
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)

        # Radio buttons
        self.radio_west = QRadioButton("West")
        self.radio_east = QRadioButton("East")
        self.radio_west.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_west)
        radio_layout.addWidget(self.radio_east)

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(self.button_ar_p, 1, 1)
        layout.addWidget(self.button_ar_n, 3, 1)
        layout.addWidget(self.button_dec_p, 2, 2)
        layout.addWidget(self.button_dec_n, 2, 0)
        layout.addLayout(speed_layout, 0, 0, 1, 3)
        layout.addLayout(radio_layout, 2, 1)

        self.setLayout(layout)
