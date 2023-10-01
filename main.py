import sys
import threading
import time
import imageio.v2 as imageio
import numpy as np

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout

from controllers.controller_arduino import ArduinoController
from controllers.controller_console import ConsoleController
from controllers.controller_figure import FigureController
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

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        left_layout.addWidget(self.console_controller)  # Add it to the left_layout

        # Create space for images
        logo = imageio.imread("icons/wellcome.png")
        self.figure_controller = FigureController(main=self, data=logo.transpose([1, 0, 2]))
        right_layout.addWidget(self.figure_controller)

        # Create space for 1d plot
        self.plot_controller = PlotController(self)
        right_layout.addWidget(self.plot_controller)

        # # Create a Plot Widget
        # self.plotWidget = pg.PlotWidget(self)
        # right_layout.addWidget(self.plotWidget)
        # self.plotWidget.setGeometry(50, 50, 700, 500)
        #
        # # Generate some data points for the curve
        # t = np.linspace(1, 100, 100)
        # x = 10+t*0.1
        # y = 20+t*0.12
        # data = np.concatenate((x, y), axis=0)
        #
        # # Add the curve to the plot
        # self.plot_x = self.plotWidget.plot(t, x, pen='b', symbol='o', symbolSize=8)
        # self.plot_y = self.plotWidget.plot(t, y, pen='r', symbol='o', symbolSize=8)
        #
        # # Set initial range for x and y axes
        # self.plotWidget.setRange(xRange=[0, 100], yRange=[np.min(data), np.max(data)])
        #
        # # Create a TextItem to display the last 'y' value with reduced font size
        # font_size = 10  # Set the desired font size
        # last_x_position = x[-1]  # X position of the last data point
        # last_y_position = y[-1]  # Y position of the last data point
        # text = pg.TextItem(f'Last Y Value: {last_y_position}', color=(255, 0, 0), anchor=(1, 1))
        # text.setFont(pg.QtGui.QFont("", font_size))  # Set font size
        # text.setPos(last_x_position, last_y_position)  # Set position to the last data point
        #
        # # Add the TextItem to the plot
        # self.plotWidget.addItem(text)

        # Connect to Arduino
        self.arduino = ArduinoController()

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
