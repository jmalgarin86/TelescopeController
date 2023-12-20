from PyQt5.QtWidgets import QGroupBox, QSizePolicy, QLabel, QLineEdit, QVBoxLayout, QGridLayout, QPushButton


class MultipictureWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Multi-picture control")
        self.main = main

        # Size policy
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        # matrix size
        matrixSizeLabel = QLabel('Matrix Size:')
        self.matrixSizeLineEdit = QLineEdit("2, 2")

        # displacement
        stepMovementLabel = QLabel('Steps Movement (AR, DEC):')
        self.stepMovementLineEdit = QLineEdit("100, 100")

        # frames
        framesLabel = QLabel('Number of Frames:')
        self.framesLineEdit = QLineEdit("5")

        # start button
        self.startButton = QPushButton("Start")
        self.startButton.setCheckable(True)

        # Create layouts for the group box
        groupBoxLayout = QGridLayout()
        groupBoxLayout.addWidget(matrixSizeLabel, 0, 0)
        groupBoxLayout.addWidget(self.matrixSizeLineEdit, 0, 1)
        groupBoxLayout.addWidget(stepMovementLabel, 1, 0)
        groupBoxLayout.addWidget(self.stepMovementLineEdit, 1, 1)
        groupBoxLayout.addWidget(framesLabel, 2, 0)
        groupBoxLayout.addWidget(self.framesLineEdit, 2, 1)
        groupBoxLayout.addWidget(self.startButton, 3, 0, 1, 2)

        self.setLayout(groupBoxLayout)



