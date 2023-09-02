from controllers.controller_arduino import ArduinoController
from widgets.widget_toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.keep_on_enable = False
        self.arduino = ArduinoController()

        self.action_arduino.triggered.connect(self.connect_arduino)
        self.action_keep_on.triggered.connect(self.keep_on)

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.arduino.serial_connection or not self.arduino.serial_connection.is_open:
                if self.arduino.connect():
                    self.action_keep_on.setEnabled(True)
                    self.main.manual_controller.setEnabled(True)
                    self.action_arduino.setStatusTip("Disconnect Arduino")
                    self.action_arduino.setToolTip("Disconnect Arduino")
                    print("Arduino connected!")
                else:
                    self.action_arduino.setChecked(False)
        else:
            self.arduino.disconnect()
            self.action_keep_on.setEnabled(False)  # Disable the "Guiding" button
            self.main.manual_controller.setEnabled(False)
            self.action_arduino.setStatusTip("Connect Arduino")
            self.action_arduino.setToolTip("Connect Arduino")
            print("Arduino disconnected!")

    def keep_on(self):
        if self.action_keep_on.isChecked():
            self.keep_on_enable = True
            self.action_keep_on.setText("Stop Guiding")
            self.arduino.start_keep_on()
            print("Tracking")
        else:
            self.keep_on_enable = False
            self.action_keep_on.setText("Start Guiding")
            self.arduino.stop_keep_on()
            print("Stop")
