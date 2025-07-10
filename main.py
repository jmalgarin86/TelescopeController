import platform
import subprocess
import sys
import threading
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from PIL import Image

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QTabWidget

from controllers.controller_arduino import ArduinoController
from controllers.controller_console import ConsoleController
from controllers.controller_joystick import JoyStickController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController
from controllers.controller_auto_control import AutoController
from controllers.controller_camera import GuidingCameraController
from widgets.widget_camera import CameraGuideWidget
from widgets.widget_figure import ImageWidget
from widgets.widget_plot import PlotWidget
from widgets.widget_histogram import HistogramWidget
from widgets.widget_calibration import CalibrationWidget


class TelescopeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_open = True
        self.setGeometry(100, 100, 1600, 900)

        # Get project path
        self.project_path = Path(__file__).parent

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
        main_layout.addLayout(left_layout, stretch=1)
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=3)

        # Create the manual control widget
        self.manual_controller = ManualController(self)
        left_layout.addWidget(self.manual_controller)

        # Create the auto control widget
        self.auto_controller = AutoController(self)
        left_layout.addWidget(self.auto_controller)

        # Create calibration controller
        self.calibration_widget = CalibrationWidget(self)
        left_layout.addWidget(self.calibration_widget)

        # Create camera widget
        self.camera_controller = CameraGuideWidget(self)
        left_layout.addWidget(self.camera_controller)

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        left_layout.addWidget(self.console_controller)  # Add it to the left_layout

        # Create space for main image
        image_path = "your_image.jpeg"
        image = Image.open(image_path)
        image_array_1 = np.array(image)
        image_path = "your_image2.jpeg"
        image = Image.open(image_path)
        image_array_2 = np.array(image)

        # Tab widget for figures
        images_tab = QTabWidget()
        self.image_guide_camera = ImageWidget(image_array=image_array_1, main=self)
        self.image_main_camera = ImageWidget(image_array=image_array_2, main=self)
        images_tab.addTab(self.image_guide_camera, "Image Guide")
        images_tab.addTab(self.image_main_camera, "Image Main")
        right_layout.addWidget(images_tab, stretch=2)

        # Layout for plots
        plots_layout = QHBoxLayout()
        right_layout.addLayout(plots_layout)

        calibration_tab = QTabWidget()
        self.plot_controller_pixel = PlotWidget(self, text='pixel')
        self.plot_controller_surface = PlotWidget(self, text='surface')
        self.histogram = HistogramWidget(self)
        calibration_tab.addTab(self.plot_controller_pixel, "Guiding plot")
        calibration_tab.addTab(self.plot_controller_surface, "Focus plot")
        calibration_tab.addTab(self.histogram, "Histogram")
        right_layout.addWidget(calibration_tab, stretch=1)

        # Connect to Arduino
        self.arduino = ArduinoController(print_command=False)

        # Connect to indiserver
        thread = threading.Thread(target=self.connect_to_indi_server)
        thread.start()
        time.sleep(1)

        # Connect to guiding camera
        self.guide_camera_controller = GuidingCameraController(self, device='Bresser GPCMOS02000KPA')

        # Create joystick controller
        JoyStickController(self)

        # Create list that contains the instructions to execute
        self.waiting_commands = []

        # Call the sniffer in a parallel thread
        thread = threading.Thread(target=self.sniffer)
        thread.start()

        self.showMaximized()

    @staticmethod
    def connect_to_indi_server():
        # Get the OS information
        system = platform.system()
        distro = ""
        if system == "Linux":
            try:
                # This will work on most modern Linux distros
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            distro = line.strip().split("=")[1].strip('"').lower()
                            break
            except FileNotFoundError:
                pass

        # Build the command based on the detected OS/distro
        if distro == "ubuntu":
            subprocess.run(["gnome-terminal", "--", "./indiserver.sh"])
        elif distro in ("raspbian", "debian"):
            subprocess.run([ "lxterminal", "--command=bash -c './indiserver.sh; exec bash'"])
        else:
            print("Unsupported OS or unknown Linux distribution.")


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
