from widgets.widget_manual_control import ManualWidget


class ManualController(ManualWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.button_ar_n.clicked.connect(self.move_ar_n)
        self.button_ar_p.clicked.connect(self.move_ar_p)
        self.button_dec_n.clicked.connect(self.move_dec_n)
        self.button_dec_p.clicked.connect(self.move_dec_p)

    def move_ar_n(self):
        if self.button_ar_n.isChecked():
            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52/speed)

            # Set command to arduino
            command = "2 0 0 0 0 "+str(period)

            # Send command
            self.main.guiding_toolbar.arduino.send_command(command)
            print("Moving AR in negative direction")
        else:
            if self.main.guiding_toolbar.keep_on_enable:
                self.main.guiding_toolbar.arduino.send_command("1 0 0 0 0 0")
                print("Tracking")
            else:
                self.main.guiding_toolbar.arduino.send_command("0 0 0 0 0 0")
                print("Stop")

        return 0

    def move_ar_p(self):
        if self.button_ar_p.isChecked():
            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52/speed)

            # Set command to arduino
            command = "2 0 1 0 0 "+str(period)

            # Send command
            self.main.guiding_toolbar.arduino.send_command(command)
            print("Moving AR in positive direction")
        else:
            if self.main.guiding_toolbar.keep_on_enable:
                self.main.guiding_toolbar.arduino.send_command("1 0 0 0 0 0")
                print("Tracking")
            else:
                self.main.guiding_toolbar.arduino.send_command("0 0 0 0 0 0")
                print("Stop")

        return 0

    def move_dec_n(self):
        if self.button_dec_n.isChecked():
            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52/speed)

            # Set command to arduino
            command = "3 0 0 0 0 "+str(period)

            # Send command
            self.main.guiding_toolbar.arduino.send_command(command)
            print("Moving DEC in negative direction")
        else:
            if self.main.guiding_toolbar.keep_on_enable:
                self.main.guiding_toolbar.arduino.send_command("1 0 0 0 0 0")
                print("Tracking")
            else:
                self.main.guiding_toolbar.arduino.send_command("0 0 0 0 0 0")
                print("Stop")

        return 0

    def move_dec_p(self):
        if self.button_dec_p.isChecked():
            # Check for speed
            speed = float(self.speed_combo.currentText()[1::])
            period = int(52/speed)

            # Set command to arduino
            command = "3 0 0 0 1 "+str(period)

            # Send command
            self.main.guiding_toolbar.arduino.send_command(command)
            print("Moving DEC in positive direction")
        else:
            if self.main.guiding_toolbar.keep_on_enable:
                self.main.guiding_toolbar.arduino.send_command("1 0 0 0 0 0")
                print("Tracking")
            else:
                self.main.guiding_toolbar.arduino.send_command("0 0 0 0 0 0")
                print("Stop")

        return 0
