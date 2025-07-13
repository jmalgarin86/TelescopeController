from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFrame, QSizePolicy


class GroupBoxWithButtonTitle(QWidget):
    button_clicked = pyqtSignal(bool)
    def __init__(self, title="My Button GroupBox"):
        super().__init__()

        # The title button
        self.title_button = QPushButton(title)
        self.title_button.setCheckable(True)  # Example: make it toggle

        # Content area
        self.content = QFrame()
        self.content.hide()
        self.content.setFrameShape(QFrame.StyledPanel)

        # Overall layout
        layout = QVBoxLayout()
        layout.addWidget(self.title_button)
        layout.addWidget(self.content)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect buttons and events
        self.title_button.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        checked = self.title_button.isChecked()
        self.button_clicked.emit(checked)
        self.content.setVisible(checked)

# Example usage
if __name__ == "__main__":
    app = QApplication([])

    widget = GroupBoxWithButtonTitle("Click Me!")
    widget.resize(300, 200)
    widget.show()

    app.exec_()
