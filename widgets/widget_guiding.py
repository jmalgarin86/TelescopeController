import sys

from PyQt5.QtWidgets import QGroupBox, QSizePolicy, QApplication, QPushButton, QLabel, QLineEdit, QGridLayout, QCheckBox


class GuidingWidget(QGroupBox):
    def __init__(self, main):
        super().__init__("Guiding")
        self.main = main

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        # Create buttons
        self.reference_button = QPushButton("Reference pixel")
        self.reference_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.set_threshold_button = QPushButton("Set threshold")
        self.set_threshold_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # Check buttons
        self.checkbox_astrophoto = QCheckBox('Astrophoto', self)

        # QLineEdits
        self.pixel_edit = QLineEdit()
        self.pixel_edit.setPlaceholderText("0, 0")
        self.threshold_edit = QLineEdit()
        self.threshold_edit.setPlaceholderText("7")

        # Layout
        layout = QGridLayout()
        layout.addWidget(self.reference_button, 0, 0)
        layout.addWidget(self.pixel_edit, 0, 1)
        layout.addWidget(self.set_threshold_button, 1, 0)
        layout.addWidget(self.threshold_edit, 1, 1)
        layout.addWidget(self.checkbox_astrophoto, 2, 0)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = GuidingWidget(0)
    x.show()
    sys.exit(app.exec_())
