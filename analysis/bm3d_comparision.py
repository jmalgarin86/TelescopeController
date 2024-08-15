import numpy as np
from astropy.io import fits
import bm3d
import time
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys


# Function to apply BM3D filter to image split into the three channels
def apply_bm3d_to_image(image, sigma):
    # Normalize image
    image_max = np.max(image)
    image = image / image_max * 100

    # Apply BM3D filter for full image by channels
    denoised_channels = []
    for channel in image:
        print("\nDenoising channel...")
        start_time = time.time()
        denoised_channel = bm3d.bm3d(channel, sigma_psd=sigma)
        denoised_channels.append(denoised_channel)
        total_time = time.time() - start_time
        print("Elapsed time: %.1f seconds" % total_time)
    denoised_image = np.stack(denoised_channels, axis=0)

    # Denormalize image
    denoised_image = denoised_image / 100 * image_max

    return denoised_image

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
fits_file = 'starless_r_pp_lights_stacked.fit'  # Update with your FITS file path
hdul = fits.open(fits_file)
image_data = hdul[0].data
image_data = image_data[:, 1000:1250, 1250:1500]
hdul[0].data = image_data
hdul.writeto('original_image.fits', overwrite=True)

# Apply BM3D filter to the image
start_time = time.time()
denoised_image_5 = apply_bm3d_to_image(image_data, sigma=1)
total_time = time.time() - start_time
print(f"\nActual time to process the entire image: {total_time:.2f} seconds")

# Apply BM3D filter to the image
start_time = time.time()
denoised_image_10 = apply_bm3d_to_image(image_data, sigma=2.5)
total_time = time.time() - start_time
print(f"\nActual time to process the entire image: {total_time:.2f} seconds")

# Apply BM3D filter to the image
start_time = time.time()
denoised_image_15 = apply_bm3d_to_image(image_data, sigma=5)
total_time = time.time() - start_time
print(f"\nActual time to process the entire image: {total_time:.2f} seconds")

# Update the FITS file with the denoised image
hdul[0].data = denoised_image_15
hdul.writeto('denoised_image.fits', overwrite=True)  # Update with your output path

# Close the FITS file
hdul.close()

# Display the original and denoised images for comparison
original_image = np.transpose(np.float64(image_data), (1, 2, 0))  # Change shape to (n, n, 3)
denoised_image_5 = np.transpose(denoised_image_5, (1, 2, 0))  # Change shape to (n, n, 3)
denoised_image_10 = np.transpose(denoised_image_10, (1, 2, 0))  # Change shape to (n, n, 3)
denoised_image_15 = np.transpose(denoised_image_15, (1, 2, 0))  # Change shape to (n, n, 3)
comparison = np.concatenate((original_image, denoised_image_5, denoised_image_10, denoised_image_15), axis=0)
display_image(comparison)
