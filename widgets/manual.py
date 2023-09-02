from PyQt5.QtWidgets import QGroupBox, QPushButton, QGridLayout, QHBoxLayout, QLabel, QComboBox, QVBoxLayout


class ManualWidget(QGroupBox):
    def __init__(self):
        super().__init__("Manual Control")

        # Initially disabled
        self.setEnabled(False)

        # Create QPushButtons
        button_ar_p = QPushButton("AR  +")
        button_ar_n = QPushButton("AR  -")
        button_dec_p = QPushButton("DEC +")
        button_dec_n = QPushButton("DEC -")

        # Create a label for the speed selection
        speed_label = QLabel("Speed")

        # Create a QComboBox for speed selection
        speed_combo = QComboBox()
        speed_combo.addItems(["x0.5", "x1", "x2", "x3", "x6", "x9", "x18", "x27"])

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(button_ar_p, 1, 1)
        layout.addWidget(button_ar_n, 3, 1)
        layout.addWidget(button_dec_p, 2, 0)
        layout.addWidget(button_dec_n, 2, 2)
        layout.addWidget(speed_label, 0, 0)
        layout.addWidget(speed_combo, 0, 1, 1, 2)

        self.setLayout(layout)
