import os
import re
import subprocess

import cv2
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt


def analyze_subframe(roi):
    if roi is None or roi.size == 0:
        return False

    # Get roi shape
    h, w = roi.shape

    # Threshold to isolate the object (binary mask)
    threshold = np.max(roi) / 2
    binary_roi = np.where(roi > threshold, 255, 0)

    # Compute center of mass
    Y, X = np.indices((h, w))
    weights = binary_roi.astype(float)
    den = np.sum(weights)

    if den == 0:
        raise ValueError("No signal detected in ROI.")

    cx = np.sum(X * weights) / den
    cy = np.sum(Y * weights) / den

    # Compute radial standard deviation
    r2 = (X - cx)**2 + (Y - cy)**2
    star_size = np.sqrt(np.sum(weights * r2) / den)

    # Coordinates of star center relative to center of ROI
    cx = cx - (w / 2)
    cy = cy - (h / 2)

    return (int(round(cx)), int(round(cy))), star_size

def run_plate_solving(file_name):
    """Execute plate-solving commands using subprocess."""
    try:
        subprocess.run([
            "solve-field", "--no-remove-lines", "--uniformize", "0", "--overwrite", "--no-plots",
            "--new-fits", "none", "--downsample", "4", "--scale-units", "arcsecperpix", "--scale-low", "0.6",
            "--scale-high", "1.0", file_name
        ], capture_output=True, text=True, timeout=5)
    except:
        print("Failed to run plate-solving.")
        return None

    # Analyse wcs generated file
    base_name = file_name.with_suffix('')
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

    print(f"RA: {ra}")
    print(f"DEC: {dec}")

    return ra, dec

def get_last_folder_in_directory(path):
    try:
        # List all directories in the given path
        directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        if not directories:
            return None
        # Sort directories lexicographically and return the last one
        directories.sort()
        last_folder = directories[-1]
        return os.path.join(path, last_folder)
    except FileNotFoundError:
        return "Path not found"
    except PermissionError:
        return "Permission denied"
    except Exception as e:
        return str(e)


def get_last_file_in_directory(path):
    try:
        # List all files in the given path
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            return None
        # Sort files lexicographically and return the last one
        files.sort(key=lambda f: os.path.getctime(os.path.join(path, f)))
        last_file = files[-1]
        return last_file
    except FileNotFoundError:
        return "Path not found"
    except PermissionError:
        return "Permission denied"
    except Exception as e:
        return str(e)

def delete_all_except_last(path):
    last_file = get_last_file_in_directory(path)

    if last_file is None:
        # print("No files to delete.")
        return
    elif isinstance(last_file, str) and ("Path not found" in last_file or "Permission denied" in last_file):
        print(last_file)
        return

    try:
        # List all files in the given path
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # Delete all files except the last one
        for file in files:
            if file != last_file:
                os.remove(os.path.join(path, file))
        # print("All files except the last one have been deleted.")
    except FileNotFoundError:
        print("Path not found")
    except PermissionError:
        print("Permission denied")
    except Exception as e:
        pass


def extract_image_matrix(file_path):
    try:
        # Open the FITS file
        with fits.open(file_path) as hdul:
            img_data = hdul[0].data  # Extract the image data from the primary HDU

        if img_data is None:
            return "No image data found in the FITS file"

        # Convert to a numpy array (ensuring it's in a proper format)
        color = cv2.cvtColor(img_data, cv2.COLOR_BayerGR2BGR)
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        image_matrix = np.clip(gray / 256 * 8, 0, 255).astype(np.uint8)
        return image_matrix
    except FileNotFoundError:
        return "File not found"
    except PermissionError:
        return "Permission denied"
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    # Create empty image
    roi = np.zeros((100, 100), dtype=np.uint8)

    # Add a bright gaussian "star"
    x0, y0 = 60, 40
    X, Y = np.meshgrid(np.arange(100), np.arange(100))
    sigma = 5
    roi += (255 * np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))).astype(np.uint8)

    # Analyze the subframe
    (center, size) = analyze_subframe(roi)

    # Show the result
    plt.imshow(roi, cmap='gray')
    plt.scatter(center[0], center[1], color='red', marker='x', label='Center of Mass')
    plt.title(f"Center: {center}, Size: {size:.2f}")
    plt.legend()
    plt.show()