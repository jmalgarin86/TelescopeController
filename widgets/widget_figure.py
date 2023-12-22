import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QMainWindow


class FigureWidget(QMainWindow):

    def __init__(self, main):
        self.main = main
        super().__init__()

        # Create a QLabel to display the webcam feed
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.view)

        # # Set up the layout
        # layout = QVBoxLayout()
        # layout.addWidget(self.view)
        #
        # # Set the layout
        # self.setLayout(layout)
