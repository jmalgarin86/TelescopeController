from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction


class MenuController:
    def __init__(self, main):
        self.main = main

        # Add menus
        menu_tasks = self.main.menu.addMenu("Tasks")

        # Create Align action
        align_action = QAction(self.main)
        align_action.setText("Align")
        align_action.triggered.connect(self.showAlignWidget)
        menu_tasks.addAction(align_action)

        # Create

    def showAlignWidget(self):
        pass