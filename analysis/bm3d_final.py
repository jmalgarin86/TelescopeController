import numpy as np
from astropy.io import fits
import bm3d
import time
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys
from skimage.util import view_as_blocks

def get_std(image, print_output=True):
    # Digitize image
    reference = np.max(image)
    image_rescaled = image / reference * 100

    # Divide the image into blocks
    n_multi = (np.array(image.shape) / 50).astype(int) * 50
    blocks = view_as_blocks(image_rescaled[0:n_multi[0], 0:n_multi[1]], block_shape=(50, 50))

    # Calculate the standard deviation for each block
    block_std_devs = np.std(blocks, axis=(2, 3))

    # Find the indices of the block with the highest entropy
    min_std_index = np.unravel_index(np.argmin(block_std_devs), block_std_devs.shape)

    # Extract the block with the highest entropy from the block_std_devs array
    std = block_std_devs[min_std_index]

    if print_output:
        print("Standard deviation for bm3d: %0.2f" % std)

    return std


def apply_bm3d_to_image(image, sigma=None, sigma_factor=1.0):
    # Function to apply BM3D filter to image split into the three channels

    # Normalize image
    image_max = np.max(image)
    image = image / image_max * 100

    # Apply BM3D filter for full image by channels
    denoised_channels = []
    for channel in image:
        if sigma is None:
            print("\nGetting std...")
            start_time = time.time()
            sigma_0 = get_std(channel)
            total_time = time.time() - start_time
            print("Elapsed time for std: %.1f seconds" % total_time)
        else:
            sigma_0 = sigma
        print("\nDenoising...")
        start_time = time.time()
        denoised_channel = bm3d.bm3d(channel, sigma_psd=sigma_0 * sigma_factor)
        denoised_channels.append(denoised_channel)
        total_time = time.time() - start_time
        print("Elapsed time for bm3d: %.1f seconds" % total_time)
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
fits_file = 'starless_stacked.fit'  # Update with your FITS file path
name = fits_file[:-4]
hdul = fits.open(fits_file)
image_data = hdul[0].data
# c, h, w = image_data.shape
# image_data = image_data[:, 1000:1300, 1000:1300]
hdul[0].data = image_data

comparison = np.transpose(np.float64(image_data), (1, 2, 0))

# Apply BM3D filter to the image
sigma_factor = [2.0]
for factor in sigma_factor:
    start_time = time.time()
    denoised_image = apply_bm3d_to_image(image_data, sigma_factor=factor)
    total_time = time.time() - start_time
    print(f"\nActual time to process the entire image: {total_time:.2f} seconds")

    # Update the FITS file with the denoised image
    hdul[0].data = (2**16*denoised_image).astype(np.uint32)
    hdul.writeto(name+'_d_'+str(factor)+'.fit', overwrite=True)  # Update with your output path

    # Add image to comparison
    denoised_image = np.transpose(denoised_image, (1, 2, 0))
    comparison = np.concatenate((comparison, denoised_image), axis=0)


# Close the FITS file
hdul.close()

# # Display the original and denoised images for comparison
# original_image = np.transpose(np.float64(image_data), (1, 2, 0))  # Change shape to (n, n, 3)
# denoised_image = np.transpose(denoised_image, (1, 2, 0))  # Change shape to (n, n, 3)
# comparison = np.concatenate((original_image, denoised_image), axis=0)
display_image(np.log10(comparison))