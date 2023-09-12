import datetime

import cv2
import numpy as np

from controllers.controller_figure import FigureController
from widgets.widget_align import AlignWidget


class AlignController(AlignWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.roi_points = None

        self.button_align.clicked.connect(self.alignImages)

    def retrieveRoi(self):
        pass

    def alignImages(self):
        # Get frames
        frames = self.main.frames
        frames_grayscale = self.main.frames_grayscale
        x = []
        y = []

        # Get roi
        idx = self.main.roi_points
        try:
            roi_data = frames_grayscale[:, idx[0]:idx[1], idx[2]:idx[3]]
        except:
            print("Frames should be 3D to be aligned")
            return

        # Match roi with frames to find the image displacement
        for frame_grayscale in frames_grayscale:
            result = cv2.matchTemplate(frame_grayscale, roi_data[self.main.roi_ind], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            x0, y0 = max_loc
            x.append(x0)
            y.append(y0)
        x = np.array(x)
        dx = x - x[0]
        y = np.array(y)
        dy = y - y[0]

        # Get the dimensions (width and height) of image2
        _, height, width = frames_grayscale.shape

        # Create an empty image of the same size as image2
        frames0_grayscale = np.zeros_like(frames_grayscale)
        frames0 = np.zeros_like(frames)

        # Align all the frames
        x1_lim = 0
        x2_lim = width
        y1_lim = 0
        y2_lim = height
        for ii in range(np.size(frames, 0)):
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
            frames0[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames[ii, y1:y2, x1:x2, :]
            frames0_grayscale[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames_grayscale[ii, y1:y2, x1:x2]

        self.main.frames = frames0[:, y1_lim:y2_lim, x1_lim:x2_lim, :]
        self.main.frames_grayscale = frames0_grayscale[:, y1_lim:y2_lim, x1_lim:x2_lim]

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
