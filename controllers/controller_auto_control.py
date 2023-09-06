import numpy as np

from widgets.widget_auto_control import AutoWidget
import threading

from catalogs.catalog import catalog

import time

class AutoController(AutoWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Atributes
        self.motor_period_x1 = 0.416  # s/step or "/step
        self.motor_period_x26 = 0.016  # s/step or "/step

        # Updtate coordinates according to first element in the catalog
        self.update_origen()
        self.update_target()

        # Connect goto button to goto function0
        self.goto_button.clicked.connect(self.goto)
        self.origen_combo.currentTextChanged.connect(self.update_origen)
        self.target_combo.currentTextChanged.connect(self.update_target)

    def update_origen(self):
        key = self.origen_combo.currentText()
        try:
            x = catalog[key]

            ar = "%sh %sm %ss" % (x[0], x[1], x[2])
            de = "%sº %s' %s''" % (x[3], x[4], x[5])

            self.ar_origin_edit.setText(ar)
            self.dec_origin_edit.setText(de)
        except:
            pass

    def update_target(self):
        key = self.target_combo.currentText()
        try:
            x = catalog[key]

            ar = "%sh %sm %ss" % (x[0], x[1], x[2])
            de = "%sº %s' %s''" % (x[3], x[4], x[5])

            self.ar_target_edit.setText(ar)
            self.dec_target_edit.setText(de)
        except:
            pass

    def get_steps(self):
        if not self.ar_origin_edit.text():
            ar_a = self.ar_origin_edit.placeholderText().split(" ")
        else:
            ar_a = self.ar_origin_edit.text().split(" ")
        ar_a = float(ar_a[0][0:-1]) * 60 * 60 + float(ar_a[1][0:-1]) * 60 + float(ar_a[2][0:-1])

        if not self.ar_target_edit.text():
            ar_b = self.ar_target_edit.placeholderText().split(" ")
        else:
            ar_b = self.ar_target_edit.text().split(" ")
        ar_b = float(ar_b[0][0:-1]) * 60 * 60 + float(ar_b[1][0:-1]) * 60 + float(ar_b[2][0:-1])

        if not self.dec_origin_edit.text():
            dec_a = self.dec_origin_edit.placeholderText().split(" ")
        else:
            dec_a = self.dec_origin_edit.text().split(" ")
        dec_a = float(dec_a[0][0:-1]) * 60 * 60 + float(dec_a[1][0:-1]) * 60 + float(dec_a[2][0:-2])

        if not self.dec_target_edit.text():
            dec_b = self.dec_target_edit.placeholderText().split(" ")
        else:
            dec_b = self.dec_target_edit.text().split(" ")
        dec_b = float(dec_b[0][0:-1]) * 60 * 60 + float(dec_b[1][0:-1]) * 60 + float(dec_b[2][0:-2])

        # Target AR
        if ar_b < ar_a:
            d_ar = np.array([ar_b - ar_a, (ar_b + 24 * 60 * 60) - ar_a])
        else:
            d_ar = np.array([ar_b - ar_a, ar_b - (ar_a + 24 * 60 * 60)])
        ar_idx = np.argmin(np.abs(d_ar))
        d_ar = d_ar[ar_idx]  # "

        # Target DEC
        d_dec = (dec_b - dec_a) * 24 / 360  # "

        return d_ar, d_dec

    def goto(self):
        thread = threading.Thread(target=self.runGoTo)
        thread.start()

    def runGoTo(self):
        bs = self.motor_period_x1
        bt = self.motor_period_x26

        # Get target coordinates
        target_ar, target_dec = self.get_steps()

        # Coordinates in steps
        nars_0 = target_ar / bs
        ndes_0 = target_dec / bs

        # Get AR position of the star at tde
        nars_tde = nars_0 - np.abs(bt / bs * ndes_0)

        # Get the AR direction
        if nars_tde >= 0:
            ar_dir = "1"
            bt = bt
        else:
            ar_dir = "0"
            bt = -bt

        # Get AR position of the star at telescope intersection
        nars_tar = bs / (bs + bt) * nars_0

        # Get the number of steps for AR axis
        nar = str(int(np.abs(np.max(np.array([nars_tar, nars_tde])))))

        # Get the DEC direction
        if self.main.manual_controller.dec_dir == 1:
            if ndes_0 >= 0:
                de_dir = "1"
            else:
                de_dir = "0"
        elif self.main.manual_controller.dec_dir == -1:
            if ndes_0 >= 0:
                de_dir = "0"
            else:
                de_dir = "1"

        # Get the number of steps for DEC axis
        nde = str(int(np.abs(ndes_0)))

        # Get time
        tar = int(nar) * bt
        tde = int(nde) * bt
        t = np.max(np.array([np.abs(tar), np.abs(tde)]))
        minutes = int(t/60)
        seconds = int(t-int(t/60))

        # Send instruction to arduino
        print("Go to the target")
        print("Time: %im %is" % (minutes, seconds))
        command = "0 %s %s %s %s 2" % (nar, ar_dir, nde, de_dir)
        self.main.waiting_commands.append(command)
        self.main.arduino.serial_connection.flushInput()
        while self.main.arduino.serial_connection.in_waiting == 0:
            time.sleep(0.01)
            pass
        self.main.arduino.serial_connection.flushInput()

        # Do tracking or not depending on tracking button status
        if self.main.guiding_toolbar.tracking_enable:
            self.main.waiting_commands.append("1 0 0 0 0 0")
            print("Tracking")
        else:
            self.main.waiting_commands.append("0 0 0 0 0 0")
            print("Stop")

        return 0
