import time

import serial
import serial.tools.list_ports


class ArduinoController:
    def __init__(self, baud_rate=19200, print_command=False):
        self.print_command = print_command
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.waiting_response = False

    def find_arduino_port(self):
        # Get a list of all available serial ports
        ports = serial.tools.list_ports.comports()

        for port in ports:
            try:
                if "Arduino" in port.manufacturer:
                    return port.device
            except:
                pass

        return None

    def connect(self):
        arduino_port = self.find_arduino_port()
        if arduino_port:
            try:
                self.serial_connection = serial.Serial(arduino_port, self.baud_rate, timeout=1)
                return True
            except Exception as e:
                print(f"Error connecting to Arduino: {str(e)}")
                return False
        else:
            print("Arduino not found. Make sure it's connected.")
            return False

    def disconnect(self):
        if self.serial_connection:
            self.serial_connection.close()

        return 0

    def send_command(self, command):
        self.waiting_response = True
        # print(command)
        if self.print_command:
            print(command)
        if self.serial_connection:
            if self.serial_connection.is_open:
                self.serial_connection.write(command.encode())
                ser_input = self.serial_connection.readline().decode('utf-8').strip()
                while ser_input != "Ready!":
                    # print("Waiting response...")
                    ser_input = self.serial_connection.readline().decode('utf-8').strip()
                    time.sleep(0.01)
                self.waiting_response = False
                # print(ser_input)
            else:
                print("Serial connection is not open.")
                ser_input = None
        else:
            print("No serial connection created.")
            ser_input = None
        self.waiting_response = False
        return ser_input

    def start_tracking(self):
        self.send_command("2 0 0 52 0 0 0\n")

    def stop_tracking(self):
        self.send_command("2 0 0 52 0 0 0\n")

