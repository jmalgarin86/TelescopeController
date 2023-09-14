from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QSizePolicy


class AberrationWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Chromatic aberration")
        self.main = main

        # Geometry constraints
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        self.hide()

        # Add QPushButtons
        self.button_rescale = QPushButton("Rescale")
        self.button_aberration = QPushButton("Fix aberration")
        label1 = QLabel("1) Rescale the image.")
        label2 = QLabel("2) Select a roi on a star.")
        label3 = QLabel("3) Click on Fix aberration button")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(self.button_rescale)
        layout.addWidget(self.button_aberration)

        self.setLayout(layout)
