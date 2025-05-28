import serial
import serial.tools.list_ports
import time


class ArduinoController2:
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """
        Initialize the serial connection to the Arduino. If port is None, auto-detect.
        """
        if port is None:
            port = self.find_arduino_port()
            if port is None:
                raise RuntimeError("No Arduino device found.")
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    @staticmethod
    def find_arduino_port():
        """
        Search for an Arduino device in the list of available serial ports.
        Returns the first matching port.
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description or "ttyACM" in port.device:
                return port.device
        return None

    def connect(self):
        """
        Connect to the Arduino board.
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # wait for Arduino to reset
            print(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")

    def disconnect(self):
        """
        Close the serial connection.
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Disconnected from Arduino.")

    def send_command(self, command):
        """
        Send a command to the Arduino.
        """
        if self.serial and self.serial.is_open:
            self.serial.write((command + '\n').encode())
            print(f"Sent: {command}")
        else:
            print("Serial connection not open.")

    def wait_for_response(self, poll_delay=0.1):
        """
        Continuously poll the serial port until a response is received.
        Returns the first non-empty response.
        """
        if not (self.serial and self.serial.is_open):
            print("Serial connection not open.")
            return None

        while True:
            if self.serial.in_waiting > 0:
                response = self.serial.readline().decode().strip()
                if response:
                    print(f"Received: {response}")
                    return response
            time.sleep(poll_delay)  # avoid tight loop

    def send_and_receive(self, command):
        """
        Send a command and wait for a response.
        """
        self.send_command(command)
        return self.wait_for_response()


class ArduinoController:
    def __init__(self, baud_rate=19200, print_command=False):
        self.print_command = print_command
        self.baud_rate = baud_rate
        self.serial_connection = None

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
        if self.print_command:
            print(command)
        if self.serial_connection:
            if self.serial_connection.is_open:
                self.serial_connection.write(command.encode())

    def start_tracking(self):
        self.send_command("0 0 0 52 0 0 0\n")

    def stop_tracking(self):
        self.send_command("0 0 0 52 0 0 0\n")

