from PyQt5.QtWidgets import QGroupBox, QLabel, QLineEdit, QGridLayout, QPushButton, QComboBox, QSizePolicy
from catalogs.catalog import catalog

class AutoWidget(QGroupBox):
    def __init__(self, main=None):
        super().__init__("Auto Control")
        self.main = main

        # Origin/Target button/label
        self.origin_button = QPushButton("Origin")
        target_label = QLabel("Target")
        ar_label = QLabel("AR")
        dec_label = QLabel("DEC")

        # QLineEdits
        self.ar_origin_edit = QLineEdit()
        self.ar_origin_edit.setPlaceholderText("0h 0m 0s")
        self.ar_target_edit = QLineEdit()
        self.ar_target_edit.setPlaceholderText("0h 0m 0s")
        self.dec_origin_edit = QLineEdit()
        self.dec_origin_edit.setPlaceholderText("0º 0' 0''")
        self.dec_target_edit = QLineEdit()
        self.dec_target_edit.setPlaceholderText("0º 0' 0''")

        self.origen_combo = QComboBox()
        self.origen_combo.addItems(list(catalog.keys()))
        self.origen_combo.setEditable(True)
        self.origen_combo.setPlaceholderText("Origen")

        self.target_combo = QComboBox()
        self.target_combo.addItems(list(catalog.keys()))
        self.target_combo.setEditable(True)
        self.target_combo.setPlaceholderText("Target")

        # QPushButtons
        self.update_button = QPushButton("Add or Update")
        self.goto_button = QPushButton("GoTo")

        # Layout
        layout = QGridLayout()
        layout.addWidget(ar_label, 2, 0)
        layout.addWidget(dec_label, 3, 0)
        layout.addWidget(self.origin_button, 0, 1)
        layout.addWidget(target_label, 0, 2)
        layout.addWidget(self.origen_combo, 1, 1)
        layout.addWidget(self.target_combo, 1, 2)
        layout.addWidget(self.ar_origin_edit, 2, 1)
        layout.addWidget(self.ar_target_edit, 2, 2)
        layout.addWidget(self.dec_origin_edit, 3, 1)
        layout.addWidget(self.dec_target_edit, 3, 2)
        layout.addWidget(self.update_button, 4, 0, 1, 3)
        layout.addWidget(self.goto_button, 5, 0, 1, 3)

        self.setLayout(layout)
