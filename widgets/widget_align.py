from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QSizePolicy


class AlignWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Image alignment")
        self.main = main

        # Geometry constraints
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.setMaximumWidth(400)
        # self.setMinimumWidth(400)
        # self.setMaximumHeight(400)
        # self.setMinimumHeight(400)

        # Add QPushButtons
        self.button_align = QPushButton("Align")
        label1 = QLabel("1) Select a roi.")
        label2 = QLabel("2) Click on Align button")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(self.button_align)

        self.setLayout(layout)
