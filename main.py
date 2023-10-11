import sys
import threading
import time
import imageio.v2 as imageio
import numpy as np

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout

from controllers.controller_arduino import ArduinoController
from controllers.controller_calibration import CalibrationController
from controllers.controller_console import ConsoleController
from controllers.controller_figure import FigureController
from controllers.controller_joystick import JoyStickController
from controllers.controller_plot import PlotController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController
from controllers.controller_auto_control import AutoController

import pyqtgraph as pg

class TelescopeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_open = True
        self.setGeometry(100, 100, 1600, 900)

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

        # Create main_layout for the central widget
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create a left_layout and right_layout
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        # Create the manual control widget
        self.manual_controller = ManualController(self)
        left_layout.addWidget(self.manual_controller)

        # Create the auto control widget
        self.auto_controller = AutoController(self)
        left_layout.addWidget(self.auto_controller)

        # Create calibration controller
        self.calibration_controller = CalibrationController(self)
        left_layout.addWidget(self.calibration_controller)

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        left_layout.addWidget(self.console_controller)  # Add it to the left_layout

        # Create space for images
        logo = imageio.imread("icons/wellcome.png")
        self.figure_controller = FigureController(main=self, data=logo.transpose([1, 0, 2]))
        right_layout.addWidget(self.figure_controller)

        # Layout for plots
        plots_layout = QHBoxLayout()
        right_layout.addLayout(plots_layout)

        # Create space for 1d plot
        self.plot_controller_x = PlotController(self, text='X')
        plots_layout.addWidget(self.plot_controller_x)

        # Create space for 1d plot
        self.plot_controller_y = PlotController(self, text='Y')
        plots_layout.addWidget(self.plot_controller_y)

        # Connect to Arduino
        self.arduino = ArduinoController()

        # Create joystick controller
        JoyStickController(self)

        # Create list that contains the instructions to execute
        self.waiting_commands = []

        # Call the sniffer in a parallel thread
        thread = threading.Thread(target=self.sniffer)
        thread.start()

        self.showMaximized()

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

# class Processing(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         # Set the stylesheet
#         style_sheet = qdarkstyle.load_stylesheet_pyqt5()
#         self.setStyleSheet(style_sheet)
#
#         # Set the window title
#         self.setWindowTitle("TelescopeController")
#
#         # Create a central widget to hold the content
#         central_widget = QWidget(self)
#         self.setCentralWidget(central_widget)
#
#         # Create archive toolbar
#         self.archive_toolbar = PrArchiveToolBarController(self, "Archive toolbar")
#
#         # Define the main layout
#         self.main_layout = QHBoxLayout()
#         central_widget.setLayout(self.main_layout)
#
#         # Show menu bar
#         self.menu = self.menuBar()
#         MenuController(main=self)
#
#         # Define the actions layout
#         self.left_layout = QVBoxLayout()
#         self.main_layout.addLayout(self.left_layout)
#
#         # Define the output layout
#         self.right_layout = QVBoxLayout()
#         self.main_layout.addLayout(self.right_layout)
#
#         # Widget for alignment
#         self.tasks_controller = TasksController(self)
#         self.left_layout.addWidget(self.tasks_controller)
#
#         # Widget with history list
#         self.history_controller = HistoryController(self)
#         self.left_layout.addWidget(self.history_controller)
#
#         # Define the figures layout
#         self.figure_layout = FiguresLayoutController()
#         self.right_layout.addWidget(self.figure_layout)
#
#         # Add spacer
#         self.left_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
#
#         # Status bar
#         self.setStatusBar(QStatusBar(self))

def main():
    app = QApplication(sys.argv)
    window = TelescopeController()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
