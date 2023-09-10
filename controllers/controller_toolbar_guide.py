from widgets.widget_toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tracking_enable = False

        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_tracking.triggered.connect(self.tracking)
        self.action_processing.triggered.connect(self.open_processing_gui)

    def open_processing_gui(self):
        self.main.pro.show()

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.main.arduino.serial_connection or not self.main.arduino.serial_connection.is_open:
                if self.main.arduino.connect():
                    self.action_tracking.setEnabled(True)
                    self.main.manual_controller.setEnabled(True)
                    self.main.auto_controller.setEnabled(True)
                    self.action_arduino.setStatusTip("Disconnect Arduino")
                    self.action_arduino.setToolTip("Disconnect Arduino")
                    print("Arduino connected!")
                else:
                    self.action_arduino.setChecked(False)
        else:
            self.main.arduino.disconnect()
            self.action_tracking.setEnabled(False)  # Disable the "Guiding" button
            self.main.manual_controller.setEnabled(False)
            self.main.auto_controller.setEnabled(False)
            self.action_arduino.setStatusTip("Connect Arduino")
            self.action_arduino.setToolTip("Connect Arduino")
            print("Arduino disconnected!")

    def tracking(self):
        if self.action_tracking.isChecked():
            self.tracking_enable = True
            self.action_tracking.setText("Stop Guiding")
            self.main.waiting_commands.append("1 0 0 0 0 52\n")
            print("Tracking")
        else:
            self.tracking_enable = False
            self.action_tracking.setText("Start Guiding")
            self.main.waiting_commands.append("0 0 0 0 0 0\n")
            print("Stop")
