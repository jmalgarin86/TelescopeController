import numpy as np
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