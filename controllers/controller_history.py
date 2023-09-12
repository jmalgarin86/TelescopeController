import numpy as np
from PyQt5.QtWidgets import QAction, QMenu

from controllers.controller_figure import FigureController
from widgets.widget_history import HistoryWidget
from controllers.controller_plot1d import Plot1DController as plot
from PyQt5.QtCore import Qt


class HistoryController(HistoryWidget):
    def __init__(self, main):
        super().__init__(main)

        self.clicked_item = None
        self.history_dictionary = {}

        self.itemDoubleClicked.connect(self.updateFigure)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, point):
        self.clicked_item = self.itemAt(point)
        if self.clicked_item is not None:
            menu = QMenu(self)

            action1 = QAction("Plot grayscale", self)
            action1.triggered.connect(self.plotGrayscale)
            menu.addAction(action1)

            action2 = QAction("Plot RGB separately", self)
            action2.triggered.connect(self.plotRGB)
            menu.addAction(action2)

            action3 = QAction("Plot RGB separately in roi", self)
            action3.triggered.connect(self.plotRGBroi)
            menu.addAction(action3)

            menu.exec_(self.mapToGlobal(point))

    def plotGrayscale(self):
        self.main.figure_layout.clearFiguresLayout()

        # Get the item text
        result = self.clicked_item.text()

        if self.history_dictionary[result]['kind'] == 'image':
            # Get data
            data = self.history_dictionary[result]['data_gra']

            # Create figure controller and show image
            figure = FigureController(main=self.main, data=data)
            self.main.figure_layout.addWidget(figure)

        else:
            print("Option not available")
            return

        # Update frames in main
        self.main.frames = self.history_dictionary[result]['data_rgb']
        self.main.frames_grayscale = self.history_dictionary[result]['data_gra']

    def plotRGB(self):
        self.main.figure_layout.clearFiguresLayout()

        # Get the item text
        result = self.clicked_item.text()

        if self.history_dictionary[result]['kind'] == 'image':
            # Get data
            data = self.history_dictionary[result]['data_rgb']

            # Create figure controller and show image
            if np.size(np.shape(data)) == 4:
                figure0 = FigureController(main=self.main, data=data[:, :, :, 0])
                figure1 = FigureController(main=self.main, data=data[:, :, :, 1])
                figure2 = FigureController(main=self.main, data=data[:, :, :, 2])
            else:
                figure0 = FigureController(main=self.main, data=data[:, :, 0])
                figure1 = FigureController(main=self.main, data=data[:, :, 1])
                figure2 = FigureController(main=self.main, data=data[:, :, 2])
            self.main.figure_layout.addWidget(figure0, 0, 0)
            self.main.figure_layout.addWidget(figure1, 1, 0)
            self.main.figure_layout.addWidget(figure2, 2, 0)

        else:
            print("Option not available")
            return

        # Update frames in main
        self.main.frames = self.history_dictionary[result]['data_rgb']
        self.main.frames_grayscale = self.history_dictionary[result]['data_gra']

    def plotRGBroi(self):
        self.main.figure_layout.clearFiguresLayout()

        # Get the item text
        result = self.clicked_item.text()

        if self.history_dictionary[result]['kind'] == 'image':
            # Get data
            data = self.history_dictionary[result]['data_rgb']

            # Create figure controller and show image
            if np.size(np.shape(data)) == 4:
                # Get roi
                idx = self.main.roi_points
                try:
                    roi_data = data[:, idx[0]:idx[1], idx[2]:idx[3], :]
                except:
                    print("Frames should be 3D to be aligned")
                    return

                # Create widgets
                figure0 = FigureController(main=self.main, data=roi_data[:, :, :, 0])
                figure1 = FigureController(main=self.main, data=roi_data[:, :, :, 1])
                figure2 = FigureController(main=self.main, data=roi_data[:, :, :, 2])
            else:
                # Get roi
                idx = self.main.roi_points
                try:
                    roi_data = data[idx[0]:idx[1], idx[2]:idx[3], :]
                except:
                    print("Frames should be 3D to be aligned")
                    return

                figure0 = FigureController(main=self.main, data=roi_data[:, :, 0])
                figure1 = FigureController(main=self.main, data=roi_data[:, :, 1])
                figure2 = FigureController(main=self.main, data=roi_data[:, :, 2])
            self.main.figure_layout.addWidget(figure0, 0, 0)
            self.main.figure_layout.addWidget(figure1, 1, 0)
            self.main.figure_layout.addWidget(figure2, 2, 0)

        else:
            print("Option not available")
            return

        # Update frames in main
        self.main.frames = self.history_dictionary[result]['data_rgb']
        self.main.frames_grayscale = self.history_dictionary[result]['data_gra']

    def updateFigure(self, item):
        # Delete widgets from figure_layout
        self.main.figure_layout.clearFiguresLayout()

        # Get the item text
        result = item.text()

        if self.history_dictionary[result]['kind'] == 'image':
            # Get data
            data = self.history_dictionary[result]['data_rgb']

            # Create figure controller and show image
            figure = FigureController(main=self.main, data=data)
            self.main.figure_layout.addWidget(figure)

        else:
            # Get data
            x_data = self.history_dictionary[result]['x_data']
            y_data = self.history_dictionary[result]['y_data']
            legend = self.history_dictionary[result]['legend']

            # Create plot widget to show curve
            noise_plot = plot(x_data=x_data, y_data=y_data, legend=legend)
            self.main.figure_layout.addWidget(noise_plot)

        # Update frames in main
        self.main.frames = self.history_dictionary[result]['data_rgb']
        self.main.frames_grayscale = self.history_dictionary[result]['data_gra']
