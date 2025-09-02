import io
import threading
import time

import PyIndi
from astropy.io import fits


class CameraController(PyIndi.BaseClient):
    def __init__(self, device="ZWO CCD ASI120MC-S", host="localhost", port=7624, timeout=1):
        super(CameraController, self).__init__()
        self.device = device
        self.host = host
        self.port = port
        self.timeout = timeout

        self.exposure = 0.01
        self.gain = 100

        self.blob_event = threading.Event()
        self.blob_event.clear()


        """Connect to the INDI server and the selected camera device."""
        # Connect to server if not already connected
        if not self.isServerConnected():
            print(f"Connecting to INDI server at {self.host}:{self.port}...")
            self.setServer(hostname=self.host, port=self.port)
            if not self.connectServer():
                print("ERROR: Could not connect to INDI server.")
            time.sleep(1)

        # Get device
        self.device_ccd = self.getDevice(self.device)
        if not self.device_ccd:
            print(f"ERROR: Device {self.device} not found.")

        # Connect to device
        if not self.device_ccd.isConnected():
            print(f"Connecting to device {self.device}...")
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")
            if ccd_connect is not None:
                ccd_connect.reset()
                ccd_connect[0].setState(PyIndi.ISS_ON)
                self.sendNewSwitch(ccd_connect)
                time.sleep(1)

        # Check connection
        if self.device_ccd.isConnected():
            print(f"{self.device} connected.")
        else:
            print(f"Failed to connect {self.device}.")

        # Get relevant properties
        self.ccd_exposure = self.device_ccd.getNumber("CCD_EXPOSURE")

        # Inform to indi server we want to receive blob from CCD1
        self.setBLOBMode(PyIndi.B_ALSO, self.device, "CCD1")

        # Get blob
        self.ccd_ccd1 = self.device_ccd.getBLOB("CCD1")
        time.sleep(1)

        print(f"{self.device} ready!")

    def updateProperty(self, prop):
        if prop.getType() == PyIndi.INDI_BLOB:
            self.blob_event.set()

    def _do_exposure(self, exposure):
        self.ccd_exposure[0].setValue(exposure)
        self.blob_event.clear()
        self.sendNewNumber(self.ccd_exposure)
        success = self.blob_event.wait(timeout=exposure + self.timeout)
        return success

    def capture(self):
        # Trigger exposure
        while not self._do_exposure(self.exposure):
            print("Exposure failed. Repeating exposure...")

        # Get fits from blob and extract image after exposure success
        blob = self.ccd_ccd1[0]
        fits_data = blob.getblobdata()  # Here is where segmentation fault eventually happens.

        # Open FITS from bytes
        hdul = fits.open(io.BytesIO(fits_data))
        image_data = hdul[0].data

        return image_data


if __name__ =='__main__':
    # client = CameraController(device="ZWO CCD ASI120MC-S", timeout=1)
    client = CameraController(device="CCD Simulator", timeout=1)
    n = 0
    while True:
        n += 1
        print(f"Getting frame {n}...")
        client.capture()