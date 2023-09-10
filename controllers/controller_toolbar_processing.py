import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from widgets.widget_toolbar_processing import ProcessingToolBarWidget
from controllers.controller_figure import FigureController


class ProcessingToolBarController(ProcessingToolBarWidget):
    def __init__(self, *args, **kwargs):
        super(ProcessingToolBarController, self).__init__(*args, **kwargs)

        self.figure_rgb = None
        self.figure_gray = None 
        self.frames_grayscale = []
        self.frames = []

        self.action_load.triggered.connect(self.load_file)
        self.action_align.triggered.connect(self.align_images)

    def align_images(self):
        roi = self.figure_rgb.align_images()

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName()

        cap = cv2.VideoCapture(file_name)

        self.frames_grayscale = []
        self.frames = []

        while True:
            # Read a frame from the video
            ret, frame = cap.read()

            # Break the loop when we reach the end of the video
            if not ret:
                break

            # Append the R frame to the list
            self.frames_grayscale.append(np.transpose(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
            self.frames.append(np.transpose(frame, [1, 0, 2]))

        cap.release()

        # Convert the list of frames into numpy arrays
        self.frames_grayscale = np.array(self.frames_grayscale)
        self.frames = np.array(self.frames)
        self.frames = self.frames[:, :, :, ::-1]

        # Create figure controller and show image
        self.figure_rgb = FigureController(self.main)
        self.main.figure_layout.addWidget(self.figure_rgb)
        self.figure_rgb.setImage(self.frames)

        # Create figure controller to show grayscale image
        self.figure_gray = FigureController(self.main)
        self.main.figure_layout.addWidget(self.figure_gray)
        self.figure_gray.setImage(self.frames_grayscale)

        return 0
