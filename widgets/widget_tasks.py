from PyQt5.QtWidgets import QGroupBox, QPushButton, QSizePolicy, QLineEdit, QGridLayout


class TasksWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Tasks")
        self.main = main

        # Geometry constraints
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        # Add QPushButtons
        self.button_dark = QPushButton("1) Apply dark")
        self.button_align = QPushButton("2) Align")
        self.button_noise = QPushButton("3) Sort by noise")
        self.button_fwhm = QPushButton("4) Sort by FHWM")
        self.text = QLineEdit()
        self.text.setPlaceholderText("0 0")
        self.button_select = QPushButton("5) Select frames")
        self.button_average = QPushButton("6) Average")
        self.button_background = QPushButton("7) Remove background")
        self.sharp = QLineEdit()
        self.sharp.setPlaceholderText("1")
        self.button_sharp = QPushButton("8) Sharpness")

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.button_dark, 0, 0, 1, 2)
        layout.addWidget(self.button_align, 1, 0, 1, 2)
        layout.addWidget(self.button_noise, 2, 0, 1, 2)
        layout.addWidget(self.button_fwhm, 3, 0, 1, 2)
        layout.addWidget(self.text, 4, 0)
        layout.addWidget(self.button_select, 4, 1)
        layout.addWidget(self.button_average, 5, 0, 1, 2)
        layout.addWidget(self.button_background, 6, 0, 1, 2)
        layout.addWidget(self.sharp, 7, 0)
        layout.addWidget(self.button_sharp, 7, 1)

        self.setLayout(layout)
