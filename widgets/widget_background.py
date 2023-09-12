from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QSizePolicy


class BackgroundWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Background")
        self.main = main

        # Geometry constraints
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        self.hide()

        # Add QPushButtons
        self.button_subtract = QPushButton("Background subtraction")
        label1 = QLabel("1) Select a roi.")
        label2 = QLabel("2) Click on Background subtraction button")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(self.button_subtract)

        self.setLayout(layout)
