from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar, QAction


class PrArchiveToolBarWidget(QToolBar):
    def __init__(self, main, *args, **kwargs):
        super(PrArchiveToolBarWidget, self).__init__(*args, **kwargs)
        self.main = main

        # Load image action button
        self.actionLoadLightFrames = QAction(QIcon("icons/light.png"), "Load light frames", self)
        self.actionLoadLightFrames.setStatusTip("Load light frames")
        self.addAction(self.actionLoadLightFrames)

        # Load image action button
        self.actionLoadDarkFrames = QAction(QIcon("icons/dark.png"), "Load dark frames", self)
        self.actionLoadDarkFrames.setStatusTip("Load light frames")
        self.addAction(self.actionLoadDarkFrames)

        # Save images
        self.actionSaveImage = QAction(QIcon("icons/save.png"), "Save frames, self")
        self.addAction(self.actionSaveImage)

        self.main.addToolBar(self)
