import datetime

import cv2
import numpy as np

from widgets.widget_background import BackgroundWidget


class BackgroundController(BackgroundWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.roi_points = None

        self.button_subtract.clicked.connect(self.subtractBackground)


    def subtractBackground(self):
        # Get frames
        frames = self.main.frames
        frames_grayscale = self.main.frames_grayscale
        x = []
        y = []

        # Get roi
        idx = self.main.roi_points
        try:
            roi_data = frames[idx[0]:idx[1], idx[2]:idx[3], :]
        except:
            print("Frames should be 2D for background subtraction")
            return

        # Get background for each channel
        b0 = np.average(frames[:, :, 0], axis=(0, 1))
        b1 = np.average(frames[:, :, 1], axis=(0, 1))
        b2 = np.average(frames[:, :, 2], axis=(0, 1))

        # Do subtraction
        frames[:, :, 0] -= b0
        frames[:, :, 1] -= b1
        frames[:, :, 2] -= b2

        self.main.frames = np.abs(frames)
        self.main.frames_grayscale = np.average(frames, axis=2)

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
