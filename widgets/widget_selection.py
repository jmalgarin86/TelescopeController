from PyQt5.QtWidgets import QGroupBox, QPushButton, QTextEdit, QGridLayout, QSizePolicy, QLineEdit


class SelectionWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Selection")
        self.main = main

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)
        self.hide()

        self.button_noise = QPushButton("Sort by noise")
        self.button_fwhm = QPushButton("Sort by FWHM")
        self.button_select = QPushButton("Select")
        self.button_avg = QPushButton("Average")

        self.text = QLineEdit()
        self.text.setPlaceholderText("0 0")

        layout = QGridLayout()
        layout.addWidget(self.button_noise, 0, 0)
        layout.addWidget(self.button_fwhm, 0, 1)
        layout.addWidget(self.text, 1, 0)
        layout.addWidget(self.button_select, 1, 1)
        layout.addWidget(self.button_avg, 2, 0, 1, 2)

        self.setLayout(layout)

