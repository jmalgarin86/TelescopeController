import pyqtgraph as pg


class FigureWidget(pg.ImageView):

    def __init__(self, main):
        self.main = main
        super().__init__()
