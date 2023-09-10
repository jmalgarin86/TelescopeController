import cv2
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


class FigureWidget(pg.ImageView):

    def __init__(self, main, *args):
        super().__init__(*args)
        self.main = main
