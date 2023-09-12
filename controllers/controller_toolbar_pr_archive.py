import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog

from controllers.controller_figure import FigureController
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

        # Delete widgets from figure_layout
        self.main.figure_layout.clearFiguresLayout()

        # Create figure controller and show image
        figure = FigureController(main=self.main, data=self.main.frames)
        self.main.figure_layout.addWidget(figure)

        return 0
