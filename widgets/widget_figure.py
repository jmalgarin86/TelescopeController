import time

from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QSizeF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QGraphicsRectItem, QGraphicsLineItem, \
    QGraphicsEllipseItem
from PyQt5.QtGui import QPixmap, QImage, QPen
import numpy as np

from utils.utils import analyze_subframe


class ImageWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setAlignment(Qt.AlignCenter)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self._zoom = 0
        self._has_loaded_image = False
        self._rect_coords = None
        self._rect_item = None
        self._image = None

    def set_image(self, image):
        if image is None:
            return None
        else:
            self._image = image

        h, w = image.shape
        bytes_per_line = w
        q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)

        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        center = QPointF(w / 2, h / 2)

        # If rectangle coords exist, add rectangle item
        if self._rect_coords is not None:
            pen = QPen(Qt.red)
            pen.setWidth(2)
            self.rect_item = QGraphicsRectItem(self._rect_coords)
            self.rect_item.setPen(pen)
            self.scene.addItem(self.rect_item)

        # Draw vertical line through image center
        pen_lines = QPen(Qt.red)  # green
        pen_lines.setWidth(2)
        vline = QGraphicsLineItem(center.x(), 0, center.x(), h)
        vline.setPen(pen_lines)
        self.scene.addItem(vline)

        # Draw horizontal line through image center
        hline = QGraphicsLineItem(0, center.y(), w, center.y())
        hline.setPen(pen_lines)
        self.scene.addItem(hline)

        # Draw circle at image center
        circle_radius = min(w, h) * 0.05  # 5% of smaller dim
        circle_rect = QRectF(center.x() - circle_radius, center.y() - circle_radius,
                             2 * circle_radius, 2 * circle_radius)
        pen_circle = QPen(Qt.red)  # blue
        pen_circle.setWidth(2)
        circle = QGraphicsEllipseItem(circle_rect)
        circle.setPen(pen_circle)
        self.scene.addItem(circle)

        if not hasattr(self, '_has_loaded_image') or not self._has_loaded_image:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            self._has_loaded_image = True

        # Return sub-image within rectangle (if exists)
        if self._rect_coords is None:
            return None

        # Clamp rectangle coordinates to image boundaries
        x = max(0, int(self._rect_coords.left()))
        y = max(0, int(self._rect_coords.top()))
        rect_w = int(self._rect_coords.width())
        rect_h = int(self._rect_coords.height())

        # Prevent going outside image
        if x + rect_w > w:
            rect_w = w - x
        if y + rect_h > h:
            rect_h = h - y

        if rect_w <= 0 or rect_h <= 0:
            return None  # Rectangle is invalid or outside image

        sub_img = image[y:y + rect_h, x:x + rect_w].copy()
        return sub_img

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        # Limit zoom level (optional)
        if self._zoom < -10:
            self._zoom = -10
            return
        elif self._zoom > 20:
            self._zoom = 20
            return

        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.LeftButton:
            # Left click: move rectangle center
            width = self._rect_coords.width() if self._rect_coords else 50
            height = self._rect_coords.height() if self._rect_coords else 50
            top_left = QPointF(scene_pos.x() - width / 2, scene_pos.y() - height / 2)
            self._rect_coords = QRectF(top_left, QSizeF(width, height))

        elif event.button() == Qt.RightButton:
            # Right click: resize rectangle keeping center fixed
            if self._rect_coords is None:
                # If no rectangle yet, create default centered at click with default size
                width, height = 20, 20
                top_left = QPointF(scene_pos.x() - width / 2, scene_pos.y() - height / 2)
                self._rect_coords = QRectF(top_left, QSizeF(width, height))
            else:
                center = self._rect_coords.center()
                # New size based on distance from center to clicked point, doubled (to get width/height)
                new_width = max(5, abs(scene_pos.x() - center.x()) * 2)
                new_height = max(5, abs(scene_pos.y() - center.y()) * 2)
                top_left = QPointF(center.x() - new_width / 2, center.y() - new_height / 2)
                self._rect_coords = QRectF(top_left, QSizeF(new_width, new_height))

        super().mousePressEvent(event)

    def get_roi_position(self):
        if self._rect_coords is None:
            return None
        center = self._rect_coords.center()

        # Return as a tuple (x, y)
        return (center.x(), center.y())

    def set_roi_position(self, position):
        x, y = position
        if self._rect_coords is None:
            # No rectangle defined yet, create a default size rectangle centered at (x, y)
            default_width = 50
            default_height = 50
            top_left = QPointF(x - default_width / 2, y - default_height / 2)
            self._rect_coords = QRectF(top_left, QSizeF(default_width, default_height))
        else:
            # Move the existing rectangle to have center at (x, y), keep size
            size = self._rect_coords.size()
            top_left = QPointF(x - size.width() / 2, y - size.height() / 2)
            self._rect_coords = QRectF(top_left, size)
        self.set_image(self._image)

class GuideImageWidget(ImageWidget):
    def __init__(self, main):
        super().__init__()

        # parameters
        self.main = main
        self._strength_ar = None
        self._strength_de = None
        self._looseness_detected = None
        self._reference_position = None
        self._guiding = None
        self._tracking = None
        self._y_vec = []
        self._x_vec = []
        self._n_dec_warnings = 0

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

    def on_guide_frame_ready(self, frame):
        # Update the frame and get the subframe for analysis
        subframe = self.set_image(frame)
        if subframe is None:
            return None

        # If tracking do the analysis
        star_size = 0
        if self._tracking:
            position = self.get_roi_position()
            star_center, star_size = analyze_subframe(subframe)
            p0 = position[0] + star_center[0]
            p1 = position[1] + star_center[1]
            position = (p0, p1)
            self.set_roi_position(position)

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

    def _align_position(self, r0=None, period=str(2)):
        # Get reference position
        if r0 is None:
            r0 = self._reference_position

        # Get current position
        r1 = self.get_roi_position()

        # Get distance
        distance = np.sqrt((r1[0] - r0[0]) ** 2 + (r1[1] - r0[1]) ** 2)
        if distance > 100:
            print("ERROR: Arduino is locked. Motors stopped.")
            self.main.waiting_commands.append("0 0 0 0 0 0 0\n")
            return 0

        # Calculate required displacement
        dr = np.array([r1[0] - r0[0], r1[1] - r0[1]])

        # Move the camera
        ser_input = self._move_camera(dx=dr[0], dy=dr[1], period=period)
        if ser_input == "Ready!":
            return ser_input
        else:
            return 0

    def _move_camera(self, dx=0, dy=0, period=str(2)):
        # Get data from calibration
        vx_de = self.main.calibration_widget.vx_de
        vy_de = self.main.calibration_widget.vy_de
        vx_ra_p = self.main.calibration_widget.vx_ar_p
        vy_ra_p = self.main.calibration_widget.vy_ar_p
        vx_ra_n = self.main.calibration_widget.vx_ar_n
        vy_ra_n = self.main.calibration_widget.vy_ar_n

        # Create matrix
        v_p = np.array([[vx_de, vx_ra_p], [vy_de, vy_ra_p]])
        v_n = np.array([[vx_de, vx_ra_n], [vy_de, vy_ra_n]])

        # Get required displacement
        dr = np.array([dx, dy])
        dr = -np.reshape(dr, (2, 1))

        # Get required steps (if n_steps[1]>0, then it is time, not steps)
        n_steps = np.linalg.inv(v_p) @ dr
        if n_steps[1] < 0:
            n_steps = np.linalg.inv(v_n) @ dr

        # Apply strength
        n_steps[0] *= self._strength_de
        n_steps[1] *= self._strength_ar

        # Ensure Dec movement happens only in the required direction
        if (self._looseness_detected == "positive" and n_steps[0] < 0) or (
                self._looseness_detected == "negative" and n_steps[0] > 0):
            n_steps[0] = 0
            self._n_dec_warnings += 1
            print("Dec warning: %i" % self._n_dec_warnings)
            # Check if looseness_detection has to switch
            if self._n_dec_warnings >= 20 and self._looseness_detected == "positive":
                self._looseness_detected = "negative"
                self._n_dec_warnings = 0
                print("Looseness direction switched to negative")
            elif self._n_dec_warnings >= 20 and self._looseness_detected == "negative":
                self._looseness_detected = "positive"
                self._n_dec_warnings = 0
                print("Looseness direction switched to positive")
        else:
            if self._n_dec_warnings > 0:
                print("Dec warning: 0")
            self._n_dec_warnings = 0
            if np.abs(n_steps[0]) > 5:
                n_steps[0] = int(n_steps[0] / 2)

        # Set directions
        if n_steps[0] >= 0 and self.main.manual_controller.dec_dir == 1:
            de_dir = str(1)
        elif n_steps[0] >= 0 and self.main.manual_controller.dec_dir == -1:
            de_dir = str(0)
        elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == 1:
            de_dir = str(0)
        elif n_steps[0] < 0 and self.main.manual_controller.dec_dir == -1:
            de_dir = str(1)
        if n_steps[1] >= 0:
            ar_dir = str(1)
        else:
            ar_dir = str(0)

        # Get instructions
        de_steps = str(int(np.abs(n_steps[0])))
        time_delay = 0
        if n_steps[1] > 0:
            ar_steps = 0
            time_delay = n_steps[1][0]
        else:
            ar_steps = str(int(np.abs(n_steps[1])))
        if de_steps == "0":
            de_command = " 0 0 0"
        else:
            de_command = " %s %s %s" % (de_steps, de_dir, period)
        if ar_steps == "0":
            ar_command = " 0 0 52"
        else:
            ar_command = " %s %s %s" % (ar_steps, ar_dir, period)

        # Send instructions
        if time_delay > 0:
            stop = "1"
        else:
            stop = "0"
        if de_steps == "0" and ar_steps == "0" and stop == "0":
            pass
            return "Ready!"
        else:
            command = "0" + ar_command + de_command + "\n"
            # Wait until it finish
            if stop == "1":
                # Move AR
                self.main.waiting_commands.append("1 0 0 0 0 0 0\n")
                time.sleep(time_delay)
                # Move DEC
                if de_command == " 0 0 0":
                    command = "0 1 0 52" + " 0 0 0" + "\n"
                    self.main.waiting_commands.append(command)
                else:
                    command = "0 0 0 52" + de_command + "\n"
                    self.main.waiting_commands.append(command)
                ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
                while ser_input != "Ready!":
                    ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
                    time.sleep(0.01)
                return "Ready!"
            else:
                self.main.waiting_commands.append(command)
                ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
                while ser_input != "Ready!":
                    ser_input = self.main.arduino.serial_connection.readline().decode('utf-8').strip()
                    time.sleep(0.01)
                return ser_input

class MainImageWidget(ImageWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self._s_vec = []

    def on_main_frame_ready(self, frame):
        subframe = self.set_image(frame)
        try:
            _, size = analyze_subframe(subframe)

            # Ensure the length of the vectors is at most 100 elements
            if len(self._s_vec) == 100:
                self._s_vec.pop(0)  # Remove the first element

            # Update vectors and plot
            self._s_vec.append(size)
            self.main.plot_controller_surface.updatePlot(x=self._s_vec)
        except:
            pass

        self.main.histogram.set_image(frame)


def load_random_image():
    # Simulate dynamic image loading (reload or random noise)
    arr = np.random.randint(0, 255, (240, 320), dtype=np.uint8)
    return arr


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    view = ImageWidget()
    view.show()

    def update_image():
        image_array = load_random_image()
        view.set_image(image_array)

    # Call update_image every 1000 ms
    timer = QTimer()
    timer.timeout.connect(update_image)
    timer.start(1000)  # in milliseconds

    sys.exit(app.exec_())
