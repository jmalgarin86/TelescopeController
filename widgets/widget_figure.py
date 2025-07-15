import threading
import time

from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Circle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import numpy as np
import sys
from PIL import Image

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='black')
        self.axes = self.fig.add_subplot(111, facecolor='black')  # Also sets axes area background
        self.axes.axis("off")
        super().__init__(self.fig)

class ImageWidget(QWidget):
    def __init__(self, image_array=None, title='Default Title', main=None):
        super().__init__()
        self.original_frame = None
        self.frame = None
        self.camera_running = False
        self.n_frame = 0
        self.exposure = 1
        self.gain = 2500

        self.setWindowTitle(title)
        self.main = main

        # Set parameters
        self._zoom_xlim = None
        self._zoom_ylim = None

        # Canvas and layout
        self._canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout = QVBoxLayout()
        layout.addWidget(self._canvas)
        self.setLayout(layout)

        # Image and ROI data
        self._image_array = None
        self._roi_center = None
        self._roi_size = 200
        self._roi_patch = None

        # Set image if provided
        if image_array is not None:
            self.set_image(image_array)

        # Connect mouse events
        self._canvas.mpl_connect("button_press_event", self._on_click)
        self._canvas.mpl_connect("scroll_event", self._on_scroll)


    def _on_click(self, event):
        if event.inaxes != self._canvas.axes:
            return

        if event.button == 1:  # Left click: set center
            self._roi_center = (event.xdata, event.ydata)
            self._draw_roi()

        elif event.button == 3:  # Right click: set size (distance from center)
            if self._roi_center is not None:
                dx = event.xdata - self._roi_center[0]
                dy = event.ydata - self._roi_center[1]
                new_half_side = max(abs(dx), abs(dy))
                self._roi_size = 2 * new_half_side
                self._draw_roi()

    def _on_scroll(self, event):
        base_scale = 1.2  # Zoom factor
        ax = self._canvas.axes

        # Get current x and y limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Get mouse position in data coordinates
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return  # Ignore scrolls outside the image

        # Calculate zoom scale
        scale_factor = base_scale if event.button == 'up' else 1 / base_scale

        # New limits
        new_xlim = [
            xdata - (xdata - xlim[0]) * scale_factor,
            xdata + (xlim[1] - xdata) * scale_factor
        ]
        new_ylim = [
            ydata - (ydata - ylim[0]) * scale_factor,
            ydata + (ylim[1] - ydata) * scale_factor
        ]
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        # Save current axis limits to retain zoom
        self._zoom_xlim = self._canvas.axes.get_xlim()
        self._zoom_ylim = self._canvas.axes.get_ylim()

        self._canvas.draw()

    def get_image(self):
        return self._image_array

    def set_image(self, image_array):
        self._image_array = image_array
        self._canvas.axes.clear()
        self._canvas.axes.axis("off")
        self._roi_patch = None
        self._canvas.axes.imshow(image_array, cmap='gray' if image_array.ndim == 2 else None)

        # Restore zoom if available
        if self._zoom_xlim and self._zoom_ylim:
            self._canvas.axes.set_xlim(self._zoom_xlim)
            self._canvas.axes.set_ylim(self._zoom_ylim)

        # Redraw crosshairs and circle at image center
        height, width = image_array.shape[:2]
        cx, cy = width / 2, height / 2

        # Draw vertical and horizontal lines
        self._canvas.axes.axvline(cx, color='red', linestyle='--', linewidth=2)
        self._canvas.axes.axhline(cy, color='red', linestyle='--', linewidth=2)

        # Draw circle at center
        center_circle = Circle((cx, cy), radius=100, color='red', linestyle='--', fill=False, linewidth=2)
        self._canvas.axes.add_patch(center_circle)

        # Draw roi
        self._draw_roi()

        # Show canvas
        self._canvas.draw()

        # Now extract pixels in ROI if ROI is set
        if self._roi_center is not None and self._roi_size is not None:
            cx_roi, cy_roi = self._roi_center
            half = self._roi_size // 2

            # Clamp coordinates to image boundaries
            x_start = max(0, int(cx_roi - half))
            x_end = min(width, int(cx_roi + half))
            y_start = max(0, int(cy_roi - half))
            y_end = min(height, int(cy_roi + half))

            roi_pixels = image_array[y_start:y_end, x_start:x_end]
            return roi_pixels
        else:
            return None

    def _draw_roi(self):
        if self._roi_center is None or self._roi_size is None:
            return

        x0 = self._roi_center[0] - self._roi_size / 2
        y0 = self._roi_center[1] - self._roi_size / 2

        # Remove old patch
        if self._roi_patch is not None:
            self._roi_patch.remove()

        self._roi_patch = Rectangle(
            (x0, y0), self._roi_size, self._roi_size,
            linewidth=2, edgecolor='red', facecolor='none'
        )
        self._canvas.axes.add_patch(self._roi_patch)
        self._canvas.draw()

    def get_roi_position(self):
        position = (int(self._roi_center[0]), int(self._roi_center[1]))
        return position

    def set_roi_position(self, position):
        self._roi_center = position
        self._draw_roi()

class GuideImageWidget(ImageWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Connect signal
        self.main.guide_camera_widget.guide_camera.signal_guide_frame_ready.connect(self._on_guide_frame_ready)

    def _on_guide_frame_ready(self, frame):
        # Update the frame and get the subframe for analysis
        subframe = self.set_image(frame)

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
            if len(self._x_vec) == 100:
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

class MainImageWidget(ImageWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Connect signal
        self.main.main_camera_widget.main_camera.signal_main_frame_ready.connect(self._on_main_frame_ready)

    def _on_main_frame_ready(self, frame):
        subframe = self.set_image(frame)
        self.main.histogram.set_image(frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load initial image
    image_path = "../your_image.jpeg"
    image = Image.open(image_path)
    image_array = np.array(image)

    # Create and show widget
    window = ImageWidget()
    window.set_image(image_array)
    window.show()
    sys.exit(app.exec_())