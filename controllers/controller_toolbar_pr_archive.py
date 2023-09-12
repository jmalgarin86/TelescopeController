import datetime

import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from widgets.widget_toolbar_pr_archive import PrArchiveToolBarWidget


class PrArchiveToolBarController(PrArchiveToolBarWidget):
    def __init__(self, *args, **kwargs):
        super(PrArchiveToolBarController, self).__init__(*args, **kwargs)

        self.figure_rgb = None
        self.figure_gray = None 
        self.main.frames_grayscale = []
        self.main.frames = []

        self.actionLoadLightFrames.triggered.connect(self.loadLightFrames)
        self.actionLoadDarkFrames.triggered.connect(self.loadDarkFrames)

    def loadDarkFrames(self):
        pass

    def loadLightFrames(self):
        file_name, _ = QFileDialog.getOpenFileName()

        cap = cv2.VideoCapture(file_name)

        self.main.frames_grayscale = []
        self.main.frames = []

        while True:
            # Read a frame from the video
            ret, frame = cap.read()

            # Break the loop when we reach the end of the video
            if not ret:
                break

            # Append the R frame to the list
            self.main.frames_grayscale.append(np.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
            self.main.frames.append(np.transpose(frame, [1, 0, 2]))

        cap.release()

        # Convert the list of frames into numpy arrays
        self.main.frames_grayscale = np.array(self.main.frames_grayscale)
        self.main.frames = np.array(self.main.frames)
        self.main.frames = self.main.frames[:, :, :, ::-1]

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