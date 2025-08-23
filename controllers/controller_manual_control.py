import time

from widgets.widget_manual_control import ManualWidget


class ManualController(ManualWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._serial_ready = False
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

            # Set command to arduino
            command = "2 0 0 " + str(period) + " 0 0 0\n"

            # Send command
            self.main.waiting_commands.append([command, "manual"])
        else:
            self.speed_combo.setEnabled(True)
            self.main.waiting_commands.append(["2 0 0 52 0 0 0\n", "manual"])

        # Wait to arduino sends "Ready!"
        while not self._serial_ready:
            time.sleep(0.01)
            continue
        self._serial_ready = False

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

            # Set command to arduino
            command = "2 0 1 " + str(period) + " 0 0 0\n"

            # Send command
            self.main.waiting_commands.append([command, "manual"])
        else:
            self.speed_combo.setEnabled(True)
            self.main.waiting_commands.append(["2 0 0 52 0 0 0\n", "manual"])

        # Wait to arduino sends "Ready!"
        while not self._serial_ready:
            time.sleep(0.01)
            continue
        self._serial_ready = False

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
                command = "2 0 0 52 0 0 " + str(period) + "\n"
            else:
                command = "2 0 0 52 0 1 " + str(period) + "\n"

            # Send command
            self.main.waiting_commands.append([command, "manual"])
        else:
            self.speed_combo.setEnabled(True)
            self.main.waiting_commands.append(["2 0 0 52 0 0 0\n", "manual"])

        # Wait to arduino sends "Ready!"
        while not self._serial_ready:
            time.sleep(0.01)
            continue
        self._serial_ready = False

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
                command = "2 0 0 52 0 1 " + str(period) + "\n"
            else:
                command = "2 0 0 52 0 0 " + str(period) + "\n"

            # Send command
            self.main.waiting_commands.append([command, "manual"])
        else:
            self.speed_combo.setEnabled(True)
            self.main.waiting_commands.append(["2 0 0 52 0 0 0\n", "manual"])

        # Wait to arduino sends "Ready!"
        while not self._serial_ready:
            time.sleep(0.01)
            continue
        self._serial_ready = False

        return 0

    def set_serial_ready(self):
        self._serial_ready = True