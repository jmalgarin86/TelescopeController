from controllers.arduino import ArduinoController
from widgets.toolbar_guide import GuideToolBar


class GuideController(GuideToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.guiding = None
        self.arduino = ArduinoController()

        self.action_arduino.triggered.connect(self.connect_arduino)

    def connect_arduino(self):
        if self.action_arduino.isChecked():
            if not self.arduino.serial_connection or not self.arduino.serial_connection.is_open:
                if self.arduino.connect():
                    self.action_guiding.setEnabled(True)
                    self.main.manual_controller.setEnabled(True)
                    self.action_arduino.setStatusTip("Disconnect Arduino")
                    self.action_arduino.setToolTip("Disconnect Arduino")
                    print("Arduino connected!")
                else:
                    self.action_arduino.setChecked(False)
        else:
            self.arduino.disconnect()
            self.action_guiding.setEnabled(False)  # Disable the "Guiding" button
            self.main.manual_controller.setEnabled(False)
            self.action_arduino.setStatusTip("Connect Arduino")
            self.action_arduino.setToolTip("Connect Arduino")
            print("Arduino disconnected!")

    def toggle_guiding(self):
        self.guiding = not self.guiding
        if self.guiding:
            self.action_guiding.setChecked(True)
            self.guiding_button.setText("Stop Guiding")
            self.arduino.start_guiding()
        else:
            self.action_guiding.setChecked(False)
            self.guiding_button.setText("Start Guiding")
            self.arduino.stop_guiding()
