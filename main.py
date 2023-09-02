import sys
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from controllers.controller_console import ConsoleController
from controllers.controller_toolbar_guide import GuideController
from controllers.controller_manual_control import ManualController


class TelescopeController(QMainWindow):
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

        # Create guiding toolbar
        self.guiding_toolbar = GuideController(self, "Guiding toolbar")

        # Create a layout for the central widget
        layout = QVBoxLayout()

        # Create the manual control widget
        self.manual_controller = ManualController(self)
        layout.addWidget(self.manual_controller)

        # Create the ConsoleController widget
        self.console_controller = ConsoleController()
        layout.addWidget(self.console_controller)  # Add it to the layout

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Initialize guiding state
        self.guiding = False

def main():
    app = QApplication(sys.argv)
    window = TelescopeController()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
