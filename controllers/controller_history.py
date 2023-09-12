from controllers.controller_figure import FigureController
from widgets.widget_history import HistoryWidget
from controllers.controller_plot1d import Plot1DController as plot


class HistoryController(HistoryWidget):
    def __init__(self, main):
        super().__init__(main)

        self.history_dictionary = {}

        self.itemDoubleClicked.connect(self.updateFigure)

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