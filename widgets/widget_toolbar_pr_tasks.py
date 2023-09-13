from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar, QAction


class PrTasksToolBarWidget(QToolBar):
    def __init__(self, main, *args, **kwargs):
        super(PrTasksToolBarWidget, self).__init__(*args, **kwargs)
        self.main = main

        # Align action button
        self.actionAlign = QAction(QIcon("icons/align.png"), "Align frames", self)
        self.actionAlign.setStatusTip("Align frames")
        self.addAction(self.actionAlign)

        # Sort action button
        self.actionSort = QAction(QIcon("icons/sort.png"), "Sort frames", self)
        self.actionSort.setStatusTip("Sort frames")
        self.addAction(self.actionSort)

        # Background action button
        self.actionBackground = QAction(QIcon("icons/background.png"), "Background", self)
        self.addAction(self.actionBackground)

        # Aberration action button
        self.actionAberration = QAction(QIcon("icons/aberration.png"), "Aberration", self)
        self.addAction(self.actionAberration)

        self.main.addToolBar(self)
