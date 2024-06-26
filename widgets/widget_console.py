"""
@author:    José Miguel Algarín
@email:     josalggui@i3m.upv.es
@affiliation:MRILab, i3M, CSIC, Valencia, Spain
"""
from PyQt5.QtWidgets import QTextEdit, QMainWindow, QSizePolicy


class ConsoleWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the console widget
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.setCentralWidget(self.console)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)
