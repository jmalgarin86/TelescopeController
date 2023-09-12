import sys
import threading
import time

import numpy as np
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout, QSizePolicy, \
    QSpacerItem, QPushButton

from controllers.controller_align import AlignController
from controllers.controller_arduino import ArduinoController
from controllers.controller_background import BackgroundController
from controllers.controller_console import ConsoleController
from controllers.controller_figures_layout import FiguresLayoutController
from controllers.controller_history import HistoryController
from controllers.controller_selection import SelectionController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController
from controllers.controller_auto_control import AutoController
from controllers.controller_toolbar_pr_archive import PrArchiveToolBarController
from controllers.controller_menu import MenuController
from controllers.controller_toolbar_pr_tasks import PrTasksToolBarController


class TelescopeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_open = True

        # Set the stylesheet
        style_sheet = qdarkstyle.load_stylesheet_pyqt5()
        self.setStyleSheet(style_sheet)

        # Set the window title
        self.setWindowTitle("TelescopeController")

        # Create a central widget to hold the content
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create guiding toolbar
        self.guiding_toolbar = GuideController(self, "Guiding toolbar")

        # Create a layout for the central widget
        layout = QVBoxLayout()

        # Create the manual control widget
        self.manual_controller = ManualController(self)
        layout.addWidget(self.manual_controller)

        # Create the auto control widget
        self.auto_controller = AutoController(self)
        layout.addWidget(self.auto_controller)

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        layout.addWidget(self.console_controller)  # Add it to the layout

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Connect to Arduino
        self.arduino = ArduinoController()

        # Create list that contains the instructions to execute
        self.waiting_commands = []

        # Call the sniffer in a parallel thread
        thread = threading.Thread(target=self.sniffer)
        thread.start()

        self.pro = Processing()

    def sniffer(self):
        while self.gui_open:
            if self.waiting_commands:
                command = self.waiting_commands.pop(0)
                self.arduino.send_command(command)
            time.sleep(0.1)

    def closeEvent(self, event):
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        self.gui_open = False
        self.arduino.stop_tracking()
        self.arduino.disconnect()
        print('\nGUI closed successfully!')
        super().closeEvent(event)

class Processing(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the stylesheet
        style_sheet = qdarkstyle.load_stylesheet_pyqt5()
        self.setStyleSheet(style_sheet)

        # Set the window title
        self.setWindowTitle("TelescopeController")

        # Create a central widget to hold the content
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create archive toolbar
        self.archive_toolbar = PrArchiveToolBarController(self, "Archive toolbar")

        # Create tasks toolbar
        self.tasks_toolbar = PrTasksToolBarController(self, "Tasks toolbar")

        # Define the main layout
        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Show menu bar
        self.menu = self.menuBar()
        MenuController(main=self)

        # Define the actions layout
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)

        # Define the output layout
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        # Widget for alignment
        self.align_controller = AlignController(self)
        self.left_layout.addWidget(self.align_controller)

        # Widget for sorting
        self.sort_controller = SelectionController(self)
        self.left_layout.addWidget(self.sort_controller)

        # Widget for background
        self.background_controller = BackgroundController(self)
        self.left_layout.addWidget(self.background_controller)

        # Widget with history list
        self.history_controller = HistoryController(self)
        self.left_layout.addWidget(self.history_controller)

        # Define the figures layout
        self.figure_layout = FiguresLayoutController()
        self.right_layout.addWidget(self.figure_layout)

        # Add spacer
        self.left_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


def main():
    app = QApplication(sys.argv)
    window = TelescopeController()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
