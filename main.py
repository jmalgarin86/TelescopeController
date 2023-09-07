import sys
import threading
import time

import qdarkstyle
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from controllers.controller_arduino import ArduinoController
from controllers.controller_console import ConsoleController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController
from controllers.controller_auto_control import AutoController


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


def main():
    app = QApplication(sys.argv)
    window = TelescopeController()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
