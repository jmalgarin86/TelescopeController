import csv
import os
from csv import excel

import numpy as np
import subprocess
import re
from astropy.io import fits

from widgets.widget_auto_control import AutoWidget
from PyQt5.QtWidgets import QFileDialog, QApplication
import threading

from catalogs.catalog import catalog

import time


def add_or_update_field(csv_file, field_name, field_values):
    """
    Adds a new field to a CSV file. If the field already exists, it updates the values.

    Args:
        csv_file (str): File name for the CSV file.
        field_name (str): Name of the field to be added or updated.
        field_values (list): List of values for the specified field.
    """
    data = {}
    fieldnames = []

    # Read existing data from CSV file
    try:
        with open(csv_file, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            fieldnames = csv_reader.fieldnames

            # Populate data dictionary with existing data
            for field in fieldnames:
                data[field] = []
            for row in csv_reader:
                for field in fieldnames:
                    data[field].append(row[field])
    except FileNotFoundError:
        pass

    # Update or add new field values
    data[field_name] = field_values

    # Write data back to CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = list(data.keys())
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csv_writer.writeheader()

        for i in range(len(field_values)):
            row_data = {key: data[key][i] for key in fieldnames}
            csv_writer.writerow(row_data)

    print(f'Field "{field_name}" has been added or updated in CSV file "{csv_file}".')


class AutoController(AutoWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Atributes
        self.motor_period_x1 = 0.104  # s/step or "/step
        self.motor_period_x26 = 0.004  # s/step or "/step

        # Updtate coordinates according to first element in the catalog
        self.update_origen()
        self.update_target()

        # Connect goto button to goto function0
        self.origin_button.clicked.connect(self.get_origin)
        self.update_button.clicked.connect(self.update_csv)
        self.goto_button.clicked.connect(self.goto)
        self.origen_combo.currentTextChanged.connect(self.update_origen)
        self.target_combo.currentTextChanged.connect(self.update_target)

    def get_origin(self):
        """
        Open a FITS file and retrieve celestial coordinates via plate-solving.
        """
        self.main.main_camera_widget.main_camera.set_frames_to_save(frames_to_save=1, path='plate_solving/')

        file_name = self._select_fits_file()
        if not file_name:
            print("No file selected for plate solving")
            return

        base_name = file_name[:-5]
        self._run_plate_solving(file_name)
        coordinates = self._extract_coordinates(base_name)
        if coordinates:
            self._update_coordinates_display(*coordinates)
            print("Plate-solving completed successfully!")
        else:
            print("Failed to extract coordinates.")

    def _select_fits_file(self):
        """Prompt the user to select a FITS file."""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly | QFileDialog.DontUseNativeDialog
        return QFileDialog.getOpenFileName(
            self, caption="Select a FITS file", directory=os.getcwd(),
            filter="FITS Files (*.fits)", options=options
        )[0]

    def _run_plate_solving(self, file_name):
        """Execute plate-solving commands using subprocess."""
        subprocess.run([
            "solve-field", "--no-remove-lines", "--uniformize", "0",
            "--overwrite", "--downsample", "4", file_name
        ])

    def _extract_coordinates(self, base_name):
        """Extract celestial coordinates from plate-solving output."""
        result = subprocess.run(["wcsinfo", f"{base_name}.wcs"], capture_output=True, text=True)
        if not result.stdout:
            return None

        patterns = {
            "ra_center_h": r"ra_center_h (\d+)",
            "ra_center_m": r"ra_center_m (\d+)",
            "ra_center_s": r"ra_center_s ([\d\.]+)",
            "dec_center_sign": r"dec_center_sign (-?\d+)",
            "dec_center_d": r"dec_center_d (\d+)",
            "dec_center_m": r"dec_center_m (\d+)",
            "dec_center_s": r"dec_center_s ([\d\.]+)"
        }

        extracted = {k: re.search(p, result.stdout) for k, p in patterns.items()}
        if None in extracted.values():
            return None

        values = {k: v.group(1) for k, v in extracted.items()}
        values['ra_center_s'] = str(round(float(values['ra_center_s'])))
        values['dec_center_s'] = str(round(float(values['dec_center_s'])))

        ra = f"{values['ra_center_h']}h {values['ra_center_m']}m {values['ra_center_s']}s"
        dec_sign = "-" if values['dec_center_sign'] == "-1" else ""
        dec = f"{dec_sign}{values['dec_center_d']}º {values['dec_center_m']}' {values['dec_center_s']}''"

        return ra, dec

    def _update_coordinates_display(self, ra, dec):
        """Update the UI with the extracted celestial coordinates."""
        self.ar_origin_edit.setText(ra)
        self.dec_origin_edit.setText(dec)

    def update_csv(self):
        csv_file = 'catalog.csv'

        # Update Origin
        field_name = self.origen_combo.currentText()
        ar = self.ar_origin_edit.text().split(" ")
        de = self.dec_origin_edit.text().split(" ")
        field_values = [ar[0][0:-1], ar[1][0:-1], ar[2][0:-1],
                        de[0][0:-1], de[1][0:-1], de[2][0:-2]]
        add_or_update_field(csv_file, field_name, field_values)
        catalog[field_name] = field_values

        # Update Target
        field_name = self.target_combo.currentText()
        ar = self.ar_target_edit.text().split(" ")
        de = self.dec_target_edit.text().split(" ")
        field_values = [ar[0][0:-1], ar[1][0:-1], ar[2][0:-1],
                        de[0][0:-1], de[1][0:-1], de[2][0:-2]]
        add_or_update_field(csv_file, field_name, field_values)
        catalog[field_name] = field_values

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

        # Get the AR direction
        if nars_0 >= 0:
            ar_dir = "1"
            bt = bt
        else:
            ar_dir = "0"
            bt = -bt

        # Get AR position of the star at telescope intersection
        nars_tar = bs / (bs + bt) * nars_0

        # Get the number of steps for AR axis
        nar = str(int(np.abs(nars_tar)))

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
        minutes = int(t / 60)
        seconds = int(t - int(t / 60) * 60)

        # Send instruction to arduino
        print("Go to the target")
        print("Time: %im %is" % (minutes, seconds))
        command = "0 %s %s 2 %s %s 2\n" % (nar, ar_dir, nde, de_dir)
        self.main.waiting_commands.append(command)

        # Wait until it finish
        ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
        while ser_input != "Ready!":
            ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
            time.sleep(0.01)
        # Print

        print("Ready!")

        return 0
