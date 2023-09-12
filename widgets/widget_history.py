from PyQt5.QtWidgets import QListWidget, QSizePolicy


class HistoryWidget(QListWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        # Geometry constraints
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

