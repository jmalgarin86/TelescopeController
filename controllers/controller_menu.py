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

        # Tasks menu
        tasks_menu = self.main.menu.addMenu("Tasks")
        for action in self.main.tasks_toolbar.actions():
            tasks_menu.addAction(action)

        # self.light_action = QAction(self.main.processing_toolbar)
        # self.light_action.setText("Load light frames")
        # self.light_action.triggered.connect(self.loadLightFrames)
        # menu_tasks.addAction(self.light_action)

        # Create Align action
        # align_action = QAction(self.main)
        # align_action.setText("Align")
        # align_action.triggered.connect(self.showAlignWidget)
        # menu_tasks.addAction(align_action)



    def showAlignWidget(self):
        pass