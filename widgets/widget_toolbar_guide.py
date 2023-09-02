from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar, QAction


class GuideToolBar(QToolBar):
    def __init__(self, main, *args, **kwargs):
        super(GuideToolBar, self).__init__(*args, **kwargs)
        self.main = main
        self.main.addToolBar(self)

        # Setup arduino button
        self.action_arduino = QAction(QIcon("icons/arduino.png"), "Connect to arduino", self)
        self.action_arduino.setStatusTip("Connect to arduino")
        self.action_arduino.setCheckable(True)
        self.addAction(self.action_arduino)

        # Setup arduino button
        self.action_keep_on = QAction(QIcon("icons/guide.png"), "Start guide", self)
        self.action_keep_on.setStatusTip("Start guide")
        self.action_keep_on.setCheckable(True)
        self.action_keep_on.setEnabled(False)
        self.addAction(self.action_keep_on)


