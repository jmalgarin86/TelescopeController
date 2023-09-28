import imageio.v2 as imageio


from widgets.widget_figures_layout import FiguresLayoutWidget
from controllers.controller_figure import FigureController


class FiguresLayoutController(FiguresLayoutWidget):
    def __init__(self):
        super().__init__()

        # Show the initial plot
        self.firstPlot()

    def firstPlot(self):
        logo = imageio.imread("icons/wellcome.png")
        self.clearFiguresLayout()
        self.figure_controller = FigureController(main=self.main, data=logo.transpose([1, 0, 2]))
        # welcome.hideAxis('bottom')
        # welcome.hideAxis('left')
        # welcome.showHistogram(False)
        # welcome.ui.menuBtn.hide()
        # welcome.ui.roiBtn.hide()
        self.addWidget(self.figure)

        pass

    def setImage(self, data=None):
        self.figure.setImage(data=data)

    def clearFiguresLayout(self):
        """
        Clear the figures layout.

        This method removes all widgets from the figures layout.

        Returns:
            None
        """
        for ii in range(self.layout.count()):
            item = self.layout.takeAt(0)
            item.widget().deleteLater()

        return None