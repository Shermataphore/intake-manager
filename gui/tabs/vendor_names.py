# ── intake-manager/gui/tabs/vendor_names.py ──────────────────────────
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PyQt5.QtCore import Qt

class VendorNamesTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        new_layout = QHBoxLayout()
        self.new_metrc_input = QLineEdit()
        self.new_dutchie_input = QLineEdit()
        new_layout.addWidget(self.new_metrc_input)
        new_layout.addWidget(self.new_dutchie_input)
        layout.addLayout(new_layout)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Mapping")
        btn_remove = QPushButton("Remove Selected")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.vendorNameTable = QTableWidget(0, 2)
        self.vendorNameTable.setHorizontalHeaderLabels(["METRC Vendor", "Dutchie Vendor"])
        self.vendorNameTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorNameTable)

        btn_save = QPushButton("Save Mappings")
        layout.addWidget(btn_save, alignment=Qt.AlignRight)
