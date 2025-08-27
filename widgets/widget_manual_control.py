import sys
import time

from PyQt5.QtWidgets import QPushButton, QGridLayout, QHBoxLayout, QLabel, QComboBox, \
    QSizePolicy, QRadioButton, QWidget, QGroupBox, QApplication

from widgets.GroupBox import GroupBoxWithButtonTitle


class ManualWidget(GroupBoxWithButtonTitle):
    def __init__(self, main):
        super().__init__("Manual Control")
        self.main = main

        # Create QPushButtons
        self.button_ar_p = QPushButton("AR  +")
        self.button_ar_n = QPushButton("AR  -")
        self.button_dec_p = QPushButton("DEC +")
        self.button_dec_n = QPushButton("DEC -")
        self.button_ar_p.setCheckable(True)
        self.button_ar_n.setCheckable(True)
        self.button_dec_p.setCheckable(True)
        self.button_dec_n.setCheckable(True)

        # Create a label for the speed selection
        speed_label = QLabel("Speed")

        # Create a QComboBox for speed selection
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["x0.5", "x1", "x2", "x4", "x13", "x26"])

        # Set the horizontal size policy for speed_label and speed_combo
        speed_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.speed_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Create QComboBox layout
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)

        # Radio buttons
        self.radio_west = QRadioButton("West")
        self.radio_east = QRadioButton("East")
        self.radio_west.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_west)
        radio_layout.addWidget(self.radio_east)

        # Create buttons layout
        layout = QGridLayout()
        layout.addWidget(self.button_ar_p, 1, 1)
        layout.addWidget(self.button_ar_n, 3, 1)
        layout.addWidget(self.button_dec_p, 2, 2)
        layout.addWidget(self.button_dec_n, 2, 0)
        layout.addLayout(speed_layout, 0, 0, 1, 3)
        layout.addLayout(radio_layout, 2, 1)

        layout.setRowStretch(layout.rowCount(), 1)

        self.content.setLayout(layout)

        self.dec_dir = None

        self.set_dec_direction()

        self.button_ar_n.clicked.connect(self.move_ar_n)
        self.button_ar_p.clicked.connect(self.move_ar_p)
        self.button_dec_n.clicked.connect(self.move_dec_n)
        self.button_dec_p.clicked.connect(self.move_dec_p)
        self.radio_east.clicked.connect(self.set_dec_direction)
        self.radio_west.clicked.connect(self.set_dec_direction)

    def set_dec_direction(self):
        if self.radio_east.isChecked():
            self.dec_dir = +1
        elif self.radio_west.isChecked():
            self.dec_dir = -1

    def move_ar_n(self):
        if self.button_ar_n.isChecked():
            # Uncheck other buttons
            self.button_ar_p.setChecked(False)
            self.button_dec_n.setChecked(False)
            self.button_dec_p.setChecked(False)
            self.speed_combo.setEnabled(False)

            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52 / speed)

            # Send command
            command = "0 0 " + str(period) + " 0 0 0\n"
            self._send_to_arduino(command)
        else:
            self.speed_combo.setEnabled(True)
            self._send_to_arduino("0 0 52 0 0 0\n")

        return 0

    def move_ar_p(self):
        if self.button_ar_p.isChecked():
            # Uncheck other buttons
            self.button_ar_n.setChecked(False)
            self.button_dec_n.setChecked(False)
            self.button_dec_p.setChecked(False)
            self.speed_combo.setEnabled(False)

            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52 / speed)

            # Send command
            command = "0 1 " + str(period) + " 0 0 0\n"
            self._send_to_arduino(command)
        else:
            self.speed_combo.setEnabled(True)
            self._send_to_arduino("0 0 52 0 0 0\n")

        return 0

    def move_dec_n(self):
        if self.button_dec_n.isChecked():
            # Uncheck other buttons
            self.button_ar_p.setChecked(False)
            self.button_ar_n.setChecked(False)
            self.button_dec_p.setChecked(False)
            self.speed_combo.setEnabled(False)

            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52 / speed)

            # Set command to arduino
            if self.dec_dir == 1:
                command = "0 0 52 0 0 " + str(period) + "\n"
            else:
                command = "0 0 52 0 1 " + str(period) + "\n"

            # Send command
            self._send_to_arduino(command)
        else:
            self.speed_combo.setEnabled(True)
            self._send_to_arduino("0 0 52 0 0 0\n")

        return 0

    def move_dec_p(self):
        if self.button_dec_p.isChecked():
            # Uncheck other buttons
            self.button_ar_p.setChecked(False)
            self.button_ar_n.setChecked(False)
            self.button_dec_n.setChecked(False)
            self.speed_combo.setEnabled(False)

            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52 / speed)

            if self.dec_dir == 1:
                command = "0 0 52 0 1 " + str(period) + "\n"
            else:
                command = "0 0 52 0 0 " + str(period) + "\n"

            # Send command
            self._send_to_arduino(command)
        else:
            self.speed_combo.setEnabled(True)
            self._send_to_arduino("0 0 52 0 0 0\n")

        return 0

    def _send_to_arduino(self, command):
        self.main.arduino.waiting_response = True
        self.main.waiting_commands.append(command)
        while self.main.arduino.waiting_response:
            time.sleep(0.01)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManualWidget(app)
    window.show()
    sys.exit(app.exec_())