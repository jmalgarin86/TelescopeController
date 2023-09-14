import cv2
import numpy as np
from PyQt5.QtWidgets import QAction, QFileDialog

from controllers.controller_figure import FigureController


class MenuController:
    def __init__(self, main):
        self.main = main

        # Archive menu
        archive_menu = self.main.menu.addMenu("Archive")
        for action in self.main.archive_toolbar.actions():
            archive_menu.addAction(action)
