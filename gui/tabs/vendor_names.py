# gui/tabs/vendor_names.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ActiveManifestTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Vendor Names Placeholder"))
