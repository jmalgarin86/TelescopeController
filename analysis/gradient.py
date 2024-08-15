import cv2
import numpy as np
from astropy.io import fits
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys


def display_image(image):
    # Create an application instance
    app = QtWidgets.QApplication(sys.argv)

    # Create a main window
    win = pg.GraphicsLayoutWidget(show=True, title="Image Display")

    # Add a view box to the main window
    view = win.addViewBox()

    # Lock the aspect ratio so the image doesn't get distorted
    view.setAspectLocked(True)

    # Convert the image to the correct format
    image_item = pg.ImageItem(image)

    # Add the image to the view box
    view.addItem(image_item)

    # Start the Qt event loop
    sys.exit(app.exec_())


# Load the FITS file
fits_file = 'denoised_image.fits'
hdul = fits.open(fits_file)
image_data = hdul[0].data
image_data = np.transpose(image_data, axes=(1, 2, 0))
max_data = np.max(image_data)
image_data = image_data / max_data * 65535
image_cv = cv2.normalize(image_data, None, 0, 65535, cv2.NORM_MINMAX).astype(np.uint16)

# Convert to grayscale
gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

# Apply Sobel operator to get the gradients in x and y directions
sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)  # Gradient in x direction
sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)  # Gradient in y direction

# Calculate the magnitude of the gradient
magnitude = cv2.magnitude(sobelx, sobely)
magnitude[magnitude == 0] = 1
magnitude = magnitude / np.max(magnitude)
image_data_1 = np.zeros_like(image_data)
image_data_2 = np.zeros_like(image_data)
image_data_3 = np.zeros_like(image_data)
for ii in range(3):
    image_data_1[:, :, ii] = image_data[:, :, ii] / (magnitude ** 0.01)
    image_data_2[:, :, ii] = image_data[:, :, ii] / (magnitude ** 0.05)
    image_data_3[:, :, ii] = image_data[:, :, ii] / (magnitude ** 0.1)

image = np.concatenate((image_data/np.max(image_data),
                        image_data_1/np.max(image_data_1),
                        image_data_2/np.max(image_data_2),
                        image_data_3/np.max(image_data_3)), axis=0)

display_image(image)

x = 1
