from widgets.widget_toolbar_pr_tasks import PrTasksToolBarWidget


class PrTasksToolBarController(PrTasksToolBarWidget):
    def __init__(self, *args, **kwargs):
        super(PrTasksToolBarController, self).__init__(*args, **kwargs)

        self.figure_rgb = None
        self.figure_gray = None
        self.main.frames_grayscale = []
        self.main.frames = []

        self.actionAlign.triggered.connect(self.alignImages)
        self.actionSort.triggered.connect(self.sortImages)

    def sortImages(self):
        self.hideAllWidgetsExcept(self.main.left_layout, self.main.sort_controller)

    def alignImages(self):
        self.hideAllWidgetsExcept(self.main.left_layout, self.main.align_controller)

    @staticmethod
    def hideAllWidgetsExcept(layout, widget_to_show):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget != widget_to_show:
                widget.hide()
            else:
                widget.show()
