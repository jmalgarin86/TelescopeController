import cv2
import numpy as np

from controllers.controller_figure import FigureController
from widgets.widget_selection import SelectionWidget
from controllers.controller_plot1d import Plot1DController as plot


class SelectionController(SelectionWidget):
    def __init__(self, *args):
        super().__init__(*args)

        self.button_noise.clicked.connect(self.sortByNoise)
        self.button_select.clicked.connect(self.selectSlices)
        self.button_avg.clicked.connect(self.averageFrames)

    def averageFrames(self):
        image = np.average(self.main.frames, 0)

        # Clear figure layout
        self.main.figure_layout.clearFiguresLayout()

        # Create figure controller and show image
        figure = FigureController(main=self.main, data=image)
        self.main.figure_layout.addWidget(figure)

        # Convert image to uint8
        image = (image / np.max(image[:]) * 255.0).astype(np.uint8)

        # Reorganize
        image = image[:, :, ::-1]
        image = np.transpose(image, [1, 0, 2])

        cv2.imwrite(filename='result.png', img=image)



    def selectSlices(self):
        text = self.text.text()
        idx = text.split(" ")
        i0 = int(idx[0])
        i1 = int(idx[1])
        self.main.roi_data = self.main.roi_data[i0:i1]
        self.main.frames = self.main.frames[i0:i1]
        self.main.frames_grayscale = self.main.frames_grayscale[i0:i1]

        # Delete widgets from figure_layout
        self.main.figure_layout.clearFiguresLayout()

        # Create figure controller and show image
        figure = FigureController(main=self.main, data=self.main.frames)
        self.main.figure_layout.addWidget(figure)

    def sortByNoise(self):
        # Get mean value of the roi
        noise = np.average(self.main.roi_data, axis=(1, 2))
        ind = np.argsort(noise)
        self.main.roi_data = self.main.roi_data[ind]
        self.main.frames = self.main.frames[ind]
        self.main.frames_grayscale = self.main.frames_grayscale[ind]
        noise = noise[ind]

        x = np.linspace(1, np.size(self.main.roi_data, 0), np.size(self.main.roi_data, 0))
        noise_plot = plot(x_data=x, y_data=[noise])
        self.main.figure_layout.clearFiguresLayout()
        self.main.figure_layout.addWidget(noise_plot)




