import datetime
import time

import cv2
import numpy as np

from controllers.controller_figure import FigureController
from widgets.widget_selection import SelectionWidget


class SelectionController(SelectionWidget):
    def __init__(self, *args):
        super().__init__(*args)

        self.button_noise.clicked.connect(self.sortByNoise)
        self.button_select.clicked.connect(self.selectSlices)
        self.button_avg.clicked.connect(self.averageFrames)

    def averageFrames(self):
        self.main.frames = np.average(self.main.frames, 0)
        self.main.frames_grayscale = np.average(self.main.frames_grayscale, 0)

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

        # Convert image_rgb to uint8
        image_rgb = (self.main.frames / np.max(self.main.frames[:]) * 255.0).astype(np.uint8)

        # Reorganize
        image_rgb = image_rgb[:, :, ::-1]
        image_rgb = np.transpose(image_rgb, [1, 0, 2])

        cv2.imwrite(filename='results/result.png', img=image_rgb)

    def selectSlices(self):
        text = self.text.text()
        idx = text.split(" ")
        i0 = int(idx[0])
        i1 = int(idx[1])
        self.main.frames = self.main.frames[i0:i1]
        self.main.frames_grayscale = self.main.frames_grayscale[i0:i1]

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

    def sortByNoise(self):
        # Get roi
        frames_grayscale = self.main.frames_grayscale
        idx = self.main.roi_points
        try:
            roi_data = frames_grayscale[:, idx[0]:idx[1], idx[2]:idx[3]]
        except:
            print("Frames should be 3D to be aligned")
            return

        # Get mean value of the roi
        noise = np.average(roi_data, axis=(1, 2))
        ind = np.argsort(noise)
        self.main.frames = self.main.frames[ind]
        self.main.frames_grayscale = self.main.frames_grayscale[ind]
        noise = noise[ind]
        x = np.linspace(1, np.size(roi_data, 0), np.size(roi_data, 0))

        # Create resulting dictionary
        result1 = {
            'kind': 'curve',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
            'x_data': x,
            'y_data': [noise],
            'legend': [''],
        }

        result2 = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Save items
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result1

        time.sleep(0.01)
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result2
