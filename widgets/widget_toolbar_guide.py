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

        # Camera button
        self.action_camera = QAction(QIcon("icons/camera.png"), "Open the camera", self)
        self.action_camera.setStatusTip("Open default camera")
        self.action_camera.setCheckable(True)
        self.addAction(self.action_camera)

        # Look for a star
        self.action_auto_star = QAction(QIcon("icons/auto-star.png"), "Select star automatically", self)
        self.addAction(self.action_auto_star)

        # Track star position
        self.action_tracking = QAction(QIcon("icons/tracking.png"), "Init tracking", self)
        self.action_tracking.setStatusTip("Init tracking")
        self.addAction(self.action_tracking)
        self.action_tracking.setCheckable(True)

        # Initialize guiding
        self.action_guide = QAction(QIcon("icons/guide.png"), "Start guide", self)
        self.action_guide.setStatusTip("Start guide")
        self.action_guide.setCheckable(True)
        self.addAction(self.action_guide)
