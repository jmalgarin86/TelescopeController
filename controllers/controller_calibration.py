import time

import numpy as np

from widgets.widget_calibration import CalibrationWidget


class CalibrationController(CalibrationWidget):
    def __init__(self, main):
        super().__init__(main)

        # Connect buttons to actions
        self.v_dec = None
        self.theta = None
        self.button_dec.clicked.connect(self.calibrateDec)
        self.button_ar_p.clicked.connect(self.calibrateArP)
        self.button_ar_n.clicked.connect(self.calibrateArN)

    def calibrateDec(self):
        print('Start DEC calibration')

        # Check for speed
        speed = float(self.main.manual_controller.speed_combo.currentText()[1::])
        period = int(52 / speed)

        # Number of steps (to be changed by an input)
        n_steps = 200

        # Get initial coordinates
        x0, y0 = self.main.figure_controller.getCoordinates()

        # Set command to arduino
        command = "0 0 0 52 "+str(n_steps)+" 0 "+str(period)+"\n"
        self.main.waiting_commands.append(command)

        # Wait until it finish
        self.main.arduino.serial_connection.flushInput()
        while self.main.arduino.serial_connection.in_waiting == 0:
            time.sleep(0.01)
            pass
        self.main.arduino.serial_connection.flushInput()

        # Get final coordinates
        x1, y1 = self.main.figure_controller.getCoordinates()

        # Get characteristics
        dx = x1 - x0
        dy = y1 - y0
        self.theta = np.arctan(dy/dx)
        self.v_dec = np.sqrt(dx ** 2 + dy ** 2) / n_steps

        self.checkbox_dec.setChecked(True)

    def calibrateArP(self):
        print('Start AR + calibration')

    def calibrateArN(self):
        print('Start AR - calibration')
