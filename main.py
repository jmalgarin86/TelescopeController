import sys
import threading
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout

from controllers.controller_arduino import ArduinoController
from controllers.controller_calibration import CalibrationController
from controllers.controller_console import ConsoleController
from controllers.controller_figure_guide import GuideCameraController
from controllers.controller_guiding import GuidingController
from controllers.controller_joystick import JoyStickController
from controllers.controller_plot import PlotController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController
from controllers.controller_auto_control import AutoController


class TelescopeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_open = True
        self.setGeometry(100, 100, 1600, 900)

        # Get project path
        self.project_path = Path(__file__).parent.parent

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

        # Create guiding controller tab
        self.guiding_controller = GuidingController(self)
        left_layout.addWidget(self.guiding_controller)

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        left_layout.addWidget(self.console_controller)  # Add it to the left_layout

        # Create space for main image
        self.guide_camera_controller = GuideCameraController(main=self)
        right_layout.addWidget(self.guide_camera_controller)

        # Layout for plots
        plots_layout = QHBoxLayout()
        right_layout.addLayout(plots_layout)

        # Create space for 1d plot
        self.plot_controller_pixel = PlotController(self, text='pixel')
        plots_layout.addWidget(self.plot_controller_pixel)

        # Create space for 1d plot
        self.plot_controller_surface = PlotController(self, text='surface')
        plots_layout.addWidget(self.plot_controller_surface)

        # Connect to Arduino
        self.arduino = ArduinoController(print_command=False)

        # Create joystick controller
        JoyStickController(self)

        # Create list that contains the instructions to execute
        self.waiting_commands = []

        # Call the sniffer in a parallel thread
        thread = threading.Thread(target=self.sniffer)
        thread.start()

        self.showMaximized()

    @staticmethod
    def shutdown_at(hour=6, minute=0):
        # Get the current time
        now = datetime.now()

        # Define the target time (6 a.m. today)
        target_time_0 = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        target_time_1 = now.replace(hour=hour, minute=minute+5, second=0, microsecond=0)

        # If it's already past 6 a.m. today, set the target to 6 a.m. the next day
        if target_time_0 <= now <= target_time_1:
            # Shutdown the computer (choose the appropriate command for your OS)
            if os.name == 'nt':  # Windows
                os.system("shutdown /s /t 0")
            elif os.name == 'posix':  # Linux or macOS
                os.system("shutdown now")

    def on_key_pressed(self, key_name):
        message = f"Key pressed: {key_name}"
        print(message)

    def sniffer(self):
        while self.gui_open:
            if self.waiting_commands:
                command = self.waiting_commands.pop(0)
                self.arduino.send_command(command)
            time.sleep(0.1)
            self.shutdown_at(hour=7, minute=0)

    def closeEvent(self, event):
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        self.gui_open = False
        self.arduino.stop_tracking()
        self.arduino.disconnect()
        print('\nGUI closed successfully!')
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = TelescopeController()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
