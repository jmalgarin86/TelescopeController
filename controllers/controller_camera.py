import PyIndi
import time
import threading

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from astropy.io import fits
import io

from utils.utils import analyze_subframe


class CameraController(PyIndi.BaseClient):
    def __init__(self, device="Bresser GPCMOS02000KPA", host="localhost", port=7624):
        super(CameraController, self).__init__()
        self.device = device
        self.host = host
        self.port = port
        self.device_ccd = None
        self.generic_properties = []
        self.blob_event = threading.Event()
        self.blob_event.clear()
        self.exposure = 1  # s
        self.gain = 100  # 0 to 5000 for Bresser GPCMOS02000KPA

    def updateProperty(self, prop):
        if prop.getType() == PyIndi.INDI_BLOB:
            self.blob_event.set()

    def connect_server(self):
        self.setServer(hostname=self.host, port=self.port)
        self.connectServer()
        time.sleep(1)

    def get_devices(self):
        device_list = self.getDevices()
        for device in device_list:
            print(f"   > {device.getDeviceName()}")

    def get_device(self):
        self.device_ccd = self.getDevice(self.device)
        ii = 10
        while ii > 0 and not self.device_ccd:
            time.sleep(0.5)
            self.device_ccd = self.getDevice(self.device)
            ii -= 1

    def connect_device(self):
        ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        ii = 10
        while ii > 0 and not ccd_connect:
            time.sleep(0.5)
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")
            ii -= 1
        if not (self.device_ccd.isConnected()):
            ccd_connect.reset()
            ccd_connect[0].setState(PyIndi.ISS_ON)  # the "CONNECT" switch
            self.sendNewSwitch(ccd_connect)

    def get_properties(self):
        generic_properties = self.device_ccd.getProperties()
        for generic_property in generic_properties:
            print(f"   > {generic_property.getName()} {generic_property.getTypeAsString()}")
            self.generic_properties.append((generic_property.getName(), generic_property.getTypeAsString()))
            if generic_property.getType() == PyIndi.INDI_TEXT:
                for widget in PyIndi.PropertyText(generic_property):
                    print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getText()}")

            if generic_property.getType() == PyIndi.INDI_NUMBER:
                for widget in PyIndi.PropertyNumber(generic_property):
                    print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getValue()}")

            if generic_property.getType() == PyIndi.INDI_SWITCH:
                for widget in PyIndi.PropertySwitch(generic_property):
                    print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getStateAsString()}")

            if generic_property.getType() == PyIndi.INDI_LIGHT:
                for widget in PyIndi.PropertyLight(generic_property):
                    print(f"       {widget.getLabel()}({widget.getLabel()}) = {widget.getStateAsString()}")

            if generic_property.getType() == PyIndi.INDI_BLOB:
                for widget in PyIndi.PropertyBlob(generic_property):
                    print(f"       {widget.getName()}({widget.getLabel()}) = <blob {widget.getSize()} bytes>")

        return 0

    def set_exposure(self, exposure):
        self.ccd_exposure[0].setValue(exposure)
        self.sendNewNumber(self.ccd_exposure)
        self.blob_event.wait()
        self.blob_event.clear()

    def set_gain(self, gain):
        self.ccd_gain[0].setValue(gain)
        self.sendNewNumber(self.ccd_gain)
        self.blob_event.clear()

    def set_ccd_capture_format(self, capture_format="INDI_RGB(RGB)"):
        # Capture format
        ccd_capture_format = self.device_ccd.getSwitch("CCD_CAPTURE_FORMAT")

        # Transfer format
        ccd_transfer_format = self.device_ccd.getSwitch("CCD_TRANSFER_FORMAT")

        # Set the format
        if capture_format == "INDI_RGB(RGB)":
            ccd_capture_format[0].setState(PyIndi.ISS_ON)
            ccd_transfer_format[0].setState(PyIndi.ISS_OFF)
            ccd_capture_format[1].setState(PyIndi.ISS_OFF)
            ccd_transfer_format[1].setState(PyIndi.ISS_ON)
        elif capture_format == "INDI_RAW(RAW 16)":
            ccd_capture_format[0].setState(PyIndi.ISS_OFF)
            ccd_transfer_format[0].setState(PyIndi.ISS_ON)
            ccd_capture_format[1].setState(PyIndi.ISS_ON)
            ccd_transfer_format[1].setState(PyIndi.ISS_OFF)
        self.sendNewSwitch(ccd_capture_format)
        self.sendNewSwitch(ccd_transfer_format)
        self.blob_event.clear()

    def capture(self, exposure=1, gain=100):
        try:
            # Trigger image acquisition
            self.set_gain(gain)
            self.set_exposure(exposure)

            # Get fits from blob and extract image
            blob = self.ccd_ccd1[0]
            fits_data = blob.getblobdata()
            hdul = fits.open(io.BytesIO(fits_data))
            image_data = hdul[0].data
            return image_data
        except:
            print(f"Capturing frame failed.")
            return None

class GuidingCameraController(QObject, CameraController):
    _frame_ready = pyqtSignal()

    def __init__(self, main, device=None, host="localhost", port=7624):
        super().__init__()
        self._n_dec_warnings = None
        self._strength_ar = None
        self._strength_de = None
        self._star_size_threshold = None
        self._looseness_detected = None
        self._s_vec = []
        self._y_vec = []
        self._x_vec = []
        self._reference_position = None
        self._tracking = False
        self._guiding = False
        self._frame = None
        self._camera_running = False
        self._n_frames = 0
        self.main = main

        # Connect signal with _update_guiding_frame
        self._frame_ready.connect(self._update_guiding_frame)

        thread = threading.Thread(target=self._frame_sniffer)
        thread.start()

    def setup_camera(self):
        # Connect to the server
        self.connect_server()

        # Get device
        self.get_device()

        # Connect to the device
        self.connect_device()

        # Reconnect everything
        self.disconnectDevice(self.device)
        self.disconnectServer()
        self.connect_server()
        self.get_device()
        self.connect_device()
        time.sleep(1)

        # Get exposure and controls properties
        self.ccd_exposure = self.device_ccd.getNumber("CCD_EXPOSURE")
        self.ccd_gain = self.device_ccd.getNumber("CCD_CONTROLS")

        # Inform to indi server we want to receive blob from CCD1
        self.setBLOBMode(PyIndi.B_ALSO, self.device, "CCD1")

        # Get blob
        self.ccd_ccd1 = self.device_ccd.getBLOB("CCD1")
        time.sleep(1)

        # Fix frame bug
        self.set_ccd_capture_format("INDI_RAW(RAW 16)")

        print(f"{self.device} ready!")

    def _frame_sniffer(self):
        while self.main.gui_open:
            if self._camera_running:
                try:
                    # Get frame
                    self._frame = self.capture(exposure=self.exposure, gain=self.gain)

                    # Multiply the image by a factor of 8, then clip to 0, 255
                    if np.max(self._frame) > 0:
                        self._frame = np.clip(self._frame * float(8) / 2 ** 16 * 2 ** 8, a_min=0, a_max=255).astype(
                            np.uint8)

                    self._n_frames += 1
                    print(f"Frame {self._n_frames}")
                except:
                    h, w = 1080, 1920
                    self._frame = np.zeros((h, w), dtype=np.uint8)

                    # Simulate a "star" as a Gaussian spot
                    x0, y0 = 960, 540  # center of image
                    x0 = np.random.randint(x0, x0 + 10)
                    y0 = np.random.randint(y0, y0 + 10)
                    X, Y = np.meshgrid(np.arange(w), np.arange(h))
                    sigma = 20  # wider star
                    self._frame += (255 * np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * sigma ** 2))).astype(np.uint8)
                    time.sleep(1)
                self._frame_ready.emit()
                time.sleep(0.1)
            else:
                time.sleep(1)

    def _update_guiding_frame(self):
        # Update the frame and get the subframe for analysis
        subframe = self.main.image_guide_camera.set_image(self._frame)

        # If tracking do the analysis
        star_size = 0
        star_center = (0, 0)
        if self._tracking:
            position = self.main.image_guide_camera.get_roi_position()
            star_center, star_size = analyze_subframe(subframe)
            p0 = position[0] + star_center[0]
            p1 = position[1] + star_center[1]
            position = (p0, p1)
            self.main.image_guide_camera.set_roi_position(position)

            # Ensure the length of the vectors is at most 100 elements
            if len(self._x_vec) == 10:
                self._x_vec.pop(0)  # Remove the first element
                self._y_vec.pop(0)

            # Update vectors and plot
            self._x_vec.append(position[0] - self._reference_position[0])
            self._y_vec.append(position[1] - self._reference_position[1])
            self.main.plot_controller_pixel.updatePlot(x=self._x_vec, y=self._y_vec)

        # if guiding, correct position
        if self._guiding:
            # Get reference position
            x_star, y_star = self._reference_position

            # Check if star size is not correct
            if star_size > self._star_size_threshold:
                print("Missed alignment, guiding star lost...")
            else:
                self._align_position(r0=(x_star, y_star))

    def start_camera(self):
        # print("Start guiding camera")
        # # Connect to the server
        # self.connect_server()
        #
        # # Get device
        # self.get_device()
        #
        # # Connect to the device
        # self.connect_device()
        #
        # # Reconnect everything
        # self.disconnectDevice(self.device)
        # self.disconnectServer()
        # self.connect_server()
        # self.get_device()
        # self.connect_device()
        # time.sleep(1)
        #
        # # Get exposure and controls properties
        # self.ccd_exposure = self.device_ccd.getNumber("CCD_EXPOSURE")
        # self.ccd_gain = self.device_ccd.getNumber("CCD_CONTROLS")
        #
        # # Inform to indi server we want to receive blob from CCD1
        # self.setBLOBMode(PyIndi.B_ALSO, self.device, "CCD1")
        #
        # # Get blob
        # self.ccd_ccd1 = self.device_ccd.getBLOB("CCD1")
        # time.sleep(1)
        #
        # # Fix frame bug
        # self.set_ccd_capture_format("INDI_RAW(RAW 16)")

        print(f"Connected to {self.device} ")
        self._camera_running = True

    def stop_camera(self):
        print("Stop guiding camera")
        self._camera_running = False

    def set_tracking(self, tracking: bool):
        self._tracking = tracking

    def set_guiding(self, guiding: bool):
        self._guiding = guiding

    def set_reference_position(self, position: tuple):
        self._reference_position = position

    def set_looseness(self, looseness):
        self._looseness_detected = looseness

    def set_strength(self, strength=1.0, axis='DEC'):
        if axis == 'DEC':
            self._strength_de = strength
        elif axis == 'AR':
            self._strength_ar = strength

if __name__ == "__main__":
    client = GuidingCameraController(main=None, device='Bresser GPCMOS02000KPA')
    client.set_gain(400)
    client.capture(exposure=1)
    print("Ready!")