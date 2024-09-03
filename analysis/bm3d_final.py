import numpy as np
from astropy.io import fits
import bm3d
import time
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys
from skimage.util import view_as_blocks
from skimage.measure import shannon_entropy
import cv2


# def increase_sharpness(image):
#     # Try to increase the image sharpenss
#
#     # Normalize image to 16 bits
#     image_max = image.max()
#     image_norm = np.uint16(image / image_max * (2 ** 16 - 1))
#
#     # Apply Gaussian blur to the image
#     low_pass = np.zeros_like(image_norm)
#     high_pass = np.zeros_like(image_norm)
#     for ii in range(image_norm.shape[0]):
#         low_pass[ii, :, :] = cv2.GaussianBlur(image_norm[ii, :, :], (9, 9), 10.0)
#         high_pass[ii, :, :] = cv2.subtract(image_norm[ii, :, :], low_pass[ii, :, :])
#     high_pass = np.float64(high_pass+1) ** 0.003
#
#     # Subtract the blurred image from the original image to create the mask
#     # resulting_image = cv2.addWeighted(image_norm, 1.0, high_pass, 1.0, 0)
#     resulting_image = image_norm / high_pass
#     resulting_image = resulting_image / (2 ** 16 - 1) * image_max
#
#     return resulting_image

def get_std(image, print_output=True):
    # Method to estimate the standard deviation of the image
    num_bins = 1000

    # Digitize image
    reference = np.max(image)
    image_rescaled = image / reference * 100
    image_quantized = np.digitize(image_rescaled, bins=np.linspace(0, 100, num_bins + 1)) - 1

    # Divide the image into blocks
    n_multi = (np.array(image_quantized.shape) / 50).astype(int) * 50
    blocks_q = view_as_blocks(image_quantized[0:n_multi[0], 0:n_multi[1]], block_shape=(50, 50))
    blocks_r = view_as_blocks(image_rescaled[0:n_multi[0], 0:n_multi[1]], block_shape=(50, 50))

    # Calculate the standard deviation for each block
    block_std_devs = np.std(blocks_r, axis=(2, 3))

    # Calculate entropy for each block
    block_entropies = np.zeros_like(blocks_q[:, :, 0, 0], dtype=np.float32)
    for ii in range(blocks_q.shape[0]):
        for jj in range(blocks_q.shape[1]):
            block = blocks_q[ii, jj, :, :]
            entropy = shannon_entropy(block)
            block_entropies[ii, jj] = entropy

    # Find the indices of the block with the highest entropy
    max_entropy_index = np.unravel_index(np.argmax(block_entropies), block_entropies.shape)

    # Extract the block with the highest entropy from the block_std_devs array
    std = block_std_devs[max_entropy_index]

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
fits_file = 'starless_cropped_r_pp_opt_rgb_r.fit'  # Update with your FITS file path
hdul = fits.open(fits_file)
image_data = hdul[0].data
image_data = image_data[:, :, :]
hdul[0].data = image_data

# Apply BM3D filter to the image
start_time = time.time()
denoised_image = apply_bm3d_to_image(image_data, sigma_factor=0.4)
total_time = time.time() - start_time
print(f"\nActual time to process the entire image: {total_time:.2f} seconds")

# Update the FITS file with the denoised image
hdul[0].data = denoised_image
hdul.writeto('denoised_image.fit', overwrite=True)  # Update with your output path

# Close the FITS file
hdul.close()

# Display the original and denoised images for comparison
original_image = np.transpose(np.float64(image_data), (1, 2, 0))  # Change shape to (n, n, 3)
denoised_image = np.transpose(denoised_image, (1, 2, 0))  # Change shape to (n, n, 3)
comparison = np.concatenate((original_image, denoised_image), axis=0)
display_image(comparison)