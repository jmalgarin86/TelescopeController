import sys

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QSpinBox, QGridLayout, QWidget, QApplication

from controllers.controller_frames import FrameSniffer
from widgets.GroupBox import GroupBoxWithButtonTitle


class MainCameraWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Main Camera")
        self.main = main
        self.captures_path = "captures"

        # === Number of Acquisitions ===
        self.num_acq_label = QLabel("Number of Acquisitions:")
        self.num_acq_input = QSpinBox()
        self.num_acq_input.setMinimum(1)
        self.num_acq_input.setMaximum(1000)
        self.num_acq_input.setValue(1)

        # === Capture Button ===
        self.capture_button = QPushButton("Capture Frames")
        self.capture_button.setCheckable(True)

        # === Layout ===
        layout = QVBoxLayout()

        grid = QGridLayout()
        grid.addWidget(self.num_acq_label, 0, 0)
        grid.addWidget(self.num_acq_input, 0, 1)
        grid.addWidget(self.capture_button, 1, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()
        self.content.setLayout(layout)

        # Create main camera controller
        self.main_camera = FrameSniffer(main=main, camera='main')

        # Connect update button to method
        self.capture_button.clicked.connect(self.capture_frames)

    def frames_ready(self):
        self.capture_button.setChecked(False)

    def capture_frames(self):
        if self.capture_button.isChecked():
            self.main_camera.set_frames_to_save(self.num_acq_input.value(), path='captures/')
        else:
            self.main_camera.set_frames_to_save(n=0, path='captures/')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.gui_open = True
    # widget = MainCameraWidget(main=main)
    widget = GuideCameraWidget(main=main)
    widget.show()
    sys.exit(app.exec_())