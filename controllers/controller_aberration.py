import datetime

import cv2
import numpy as np

from widgets.widget_aberration import AberrationWidget


class AberrationController(AberrationWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.button_aberration.clicked.connect(self.fixAberration)
        self.button_rescale.clicked.connect(self.rescaleImage)

    def rescaleImage(self):
        frames = self.main.frames
        k_space = np.fft.fftshift(np.fft.fftn(np.fft.fftshift(frames)))

        a = frames.shape

        k_space0 = np.zeros((a[0]*4, a[1]*4, a[2]), dtype=complex)
        k_space0[int(a[0]*3/2):int(a[0]*5/2), int(a[1]*3/2):int(a[1]*5/2), :] = k_space
        frames0 = np.abs(np.fft.ifftshift(np.fft.ifftn(np.fft.ifftshift(k_space0))))

        self.main.frames = frames0

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result


    @staticmethod
    # Calculate the center of mass for each channel
    def find_center_of_mass(points, data):
        # Calculate the moments for the channel
        prov0 = data * points[0, :, :]
        prov1 = data * points[1, :, :]
        cx = np.sum(prov0) / np.sum(data)
        cy = np.sum(prov1) / np.sum(data)

        return cx, cy

    def fixAberration(self):
        # Get frames
        frames = self.main.frames
        x = []
        y = []

        # Get roi
        points = self.main.roi_coords
        idx = self.main.roi_points
        try:
            roi_data = frames[idx[0]:idx[1], idx[2]:idx[3], :]
        except:
            print("Frame should be 2D image")
            return

        for c in range(3):
            data = roi_data[:, :, c]
            x0, y0 = self.find_center_of_mass(points, data)
            x.append(x0)
            y.append(y0)

        x = np.array(x)
        dx = np.round(x - x[0]).astype(int)
        y = np.array(y)
        dy = np.round(y - y[0]).astype(int)

        # Get the dimensions (width and height) of image2
        height, width, depth = frames.shape

        # Create an empty image of the same size as image2
        frames0 = np.zeros_like(frames)

        # Align all the frames
        x1_lim = 0
        x2_lim = width
        y1_lim = 0
        y2_lim = height
        for ii in range(np.size(frames, 2)):
            # Calculate the new coordinates for image2 after shifting
            x1 = max(0, dx[ii])  # Ensure x1 is not negative
            x2 = min(width + dx[ii], width)  # Ensure x2 does not exceed the width
            y1 = max(0, dy[ii])  # Ensure y1 is not negative
            y2 = min(height + dy[ii], height)  # Ensure y2 does not exceed the height

            # Calculate the region in image1 where image2 will be placed
            x1_dst = max(0, -dx[ii])  # Destination coordinates
            x2_dst = min(width, width - dx[ii])
            y1_dst = max(0, -dy[ii])
            y2_dst = min(height, height - dy[ii])

            # Check for boundaries
            if x1_dst > x1_lim:
                x1_lim = x1_dst
            if x2_dst < x2_lim:
                x2_lim = x2_dst
            if y1_dst > y1_lim:
                y1_lim = y1_dst
            if y2_dst < y2_lim:
                y2_lim = y2_dst

            # Copy the shifted region from image2 to the corresponding region in shifted_image2
            frames0[y1_dst:y2_dst, x1_dst:x2_dst, ii] = frames[y1:y2, x1:x2, ii]
        #
        self.main.frames = frames0[y1_lim:y2_lim, x1_lim:x2_lim, :]

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

        return 0
