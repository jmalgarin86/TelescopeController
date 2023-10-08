import serial
import serial.tools.list_ports


class ArduinoController:
    def __init__(self, baud_rate=115200):
        self.baud_rate = baud_rate
        self.serial_connection = None

    def find_arduino_port(self):
        # Get a list of all available serial ports
        ports = serial.tools.list_ports.comports()

        for port in ports:
            if "Arduino" in port.description:
                return port.device

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
        if self.serial_connection:
            if self.serial_connection.is_open:
                self.serial_connection.write(command.encode())

    def start_tracking(self):
        self.send_command("0 0 0 52 0 0 0")

    def stop_tracking(self):
        self.send_command("0 0 0 0 0 0 0")

