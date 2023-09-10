from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar, QAction


class ProcessingToolBarWidget(QToolBar):
    def __init__(self, main, *args, **kwargs):
        super(ProcessingToolBarWidget, self).__init__(*args, **kwargs)
        self.main = main
        self.main.addToolBar(self)

        # Load image action button
        self.action_load = QAction(QIcon("icons/load.png"), "Load video file", self)
        self.action_load.setStatusTip("Load video file")
        self.addAction(self.action_load)

        # Align action button
        self.action_align = QAction(QIcon("icons/goto.png"), "Align images", self)
        self.action_align.setStatusTip("Align images")
        self.addAction(self.action_align)
