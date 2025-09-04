import platform
import subprocess
import sys
import threading
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QTabWidget

from controllers.controller_arduino import ArduinoController
from controllers.controller_frames import FrameSniffer
from widgets.widget_console import ConsoleWidget
from widgets.widget_toolbar_guide import GuideToolBar
from widgets.widget_manual_control import ManualWidget
from widgets.widget_auto_control import AutoWidget
from widgets.widget_camera import MainCameraWidget
from widgets.widget_figure import MainImageWidget, GuideImageWidget
from widgets.widget_plot import PlotWidget
from widgets.widget_histogram import HistogramWidget
from widgets.widget_calibration import CalibrationWidget


class TelescopeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_open = True
        self.waiting_response = False
        self.setGeometry(100, 100, 1600, 900)

        # Get project path
        self.project_path = Path(__file__).parent

        # Set the stylesheet
        style_sheet = qdarkstyle.load_stylesheet_pyqt5()
        self.setStyleSheet(style_sheet)

        # Set the window title
        self.setWindowTitle("TelescopeController")

        # Create the ConsoleWidget widget
        self.console_widget = ConsoleWidget()

        # Create list that contains the instructions to execute
        self.waiting_commands = []

        # Call the sniffer in a parallel thread
        thread = threading.Thread(target=self.sniffer)
        thread.start()

        # Connect to Arduino
        self.arduino = ArduinoController(print_command=False)

        # Create a central widget to hold the content
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create guiding toolbar
        self.guiding_toolbar = GuideToolBar(self, "Guiding toolbar")

        # Create main_layout for the central widget
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create a left_layout and right_layout
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Create the manual control widget
        self.manual_widget = ManualWidget(self)
        self.manual_widget.button_clicked.connect(self.hide_manual)

        # Create the auto control widget
        self.auto_widget = AutoWidget(self)
        self.auto_widget.button_clicked.connect(self.hide_auto)

        # Create calibration controller
        self.calibration_widget = CalibrationWidget(self)
        self.calibration_widget.button_clicked.connect(self.hide_calibration)

        # Create camera widget
        self.guide_camera_widget = FrameSniffer(main=self, camera='guide')

        # Create main camera widget
        self.main_camera_widget = MainCameraWidget(main=self)

        # Create the layout
        left_layout.addWidget(self.manual_widget)
        left_layout.addWidget(self.auto_widget)
        left_layout.addWidget(self.calibration_widget)
        left_layout.addWidget(self.main_camera_widget)
        left_layout.addWidget(self.console_widget, stretch=1)  # Add it to the left_layout
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)

        # Tab widget for figures
        images_tab = QTabWidget()
        self.image_guide_camera = GuideImageWidget(main=self)
        self.image_main_camera = MainImageWidget(main=self)
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

        self.showMaximized()

    def hide_manual(self, my_bool):
        if my_bool:
            self.auto_widget.title_button.setChecked(not my_bool)
            self.auto_widget.on_button_clicked()
            self.calibration_widget.title_button.setChecked(not my_bool)
            self.calibration_widget.on_button_clicked()
            self.main_camera_widget.title_button.setChecked(not my_bool)
            self.main_camera_widget.on_button_clicked()

    def hide_auto(self, my_bool):
        if my_bool:
            self.manual_widget.title_button.setChecked(not my_bool)
            self.manual_widget.on_button_clicked()
            self.calibration_widget.title_button.setChecked(not my_bool)
            self.calibration_widget.on_button_clicked()
            self.main_camera_widget.title_button.setChecked(not my_bool)
            self.main_camera_widget.on_button_clicked()

    def hide_calibration(self, my_bool):
        if my_bool:
            self.manual_widget.title_button.setChecked(not my_bool)
            self.manual_widget.on_button_clicked()
            self.auto_widget.title_button.setChecked(not my_bool)
            self.auto_widget.on_button_clicked()
            self.main_camera_widget.title_button.setChecked(not my_bool)
            self.main_camera_widget.on_button_clicked()

    def hide_main(self, my_bool):
        if my_bool:
            self.manual_widget.title_button.setChecked(not my_bool)
            self.manual_widget.on_button_clicked()
            self.auto_widget.title_button.setChecked(not my_bool)
            self.auto_widget.on_button_clicked()
            self.calibration_widget.title_button.setChecked(not my_bool)
            self.calibration_widget.on_button_clicked()

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
                self.waiting_response = True
                in_waiting = self.waiting_commands.pop(0)
                self.arduino.send_command(in_waiting)
                self.waiting_response = False
            time.sleep(0.01)

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
