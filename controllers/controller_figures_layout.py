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
        welcome = FigureController(main=self, data=logo.transpose([1, 0, 2]))
        # welcome.hideAxis('bottom')
        # welcome.hideAxis('left')
        # welcome.showHistogram(False)
        # welcome.ui.menuBtn.hide()
        # welcome.ui.roiBtn.hide()
        self.addWidget(welcome)

        pass

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