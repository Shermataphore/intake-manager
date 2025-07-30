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
        # Load existing mappings when the tab initializes
        self.load_vendor_names()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        new_layout = QHBoxLayout()
        self.new_metrc_input = QLineEdit()
        self.new_dutchie_input = QLineEdit()
        new_layout.addWidget(self.new_metrc_input)
        new_layout.addWidget(self.new_dutchie_input)
        layout.addLayout(new_layout)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Mapping")
        self.btn_remove = QPushButton("Remove Selected")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        layout.addLayout(btn_layout)

        self.vendorNameTable = QTableWidget(0, 2)
        self.vendorNameTable.setHorizontalHeaderLabels(["METRC Vendor", "Dutchie Vendor"])
        self.vendorNameTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorNameTable)

        self.btn_save = QPushButton("Save Mappings")
        layout.addWidget(self.btn_save, alignment=Qt.AlignRight)

        # Connect buttons to their handlers
        self.btn_add.clicked.connect(self.add_vendor_mapping)
        self.btn_remove.clicked.connect(self.remove_selected_mappings)
        self.btn_save.clicked.connect(self.save_vendor_names)

    def load_vendor_names(self):
        """Populate the table with vendor mappings from the database."""
        self.vendorNameTable.setRowCount(0)
        cur = self.conn.cursor()
        for r, (metrc, dutchie) in enumerate(
            cur.execute(
                "SELECT metrc_vendor, dutchie_vendor FROM vendor_names"
            )
        ):
            self.vendorNameTable.insertRow(r)
            itm_m = QTableWidgetItem(metrc)
            itm_m.setTextAlignment(Qt.AlignCenter)
            itm_d = QTableWidgetItem(dutchie)
            itm_d.setTextAlignment(Qt.AlignCenter)
            self.vendorNameTable.setItem(r, 0, itm_m)
            self.vendorNameTable.setItem(r, 1, itm_d)

    def add_vendor_mapping(self):
        """Add the text fields as a new mapping row in the table."""
        metrc = self.new_metrc_input.text().strip()
        dutchie = self.new_dutchie_input.text().strip()
        if not metrc or not dutchie:
            QMessageBox.warning(
                self, "Missing input", "Please enter both METRC and Dutchie names."
            )
            return
        r = self.vendorNameTable.rowCount()
        self.vendorNameTable.insertRow(r)
        item_m = QTableWidgetItem(metrc)
        item_m.setTextAlignment(Qt.AlignCenter)
        self.vendorNameTable.setItem(r, 0, item_m)
        item_d = QTableWidgetItem(dutchie)
        item_d.setTextAlignment(Qt.AlignCenter)
        self.vendorNameTable.setItem(r, 1, item_d)
        self.new_metrc_input.clear()
        self.new_dutchie_input.clear()

    def remove_selected_mappings(self):
        """Remove the currently selected rows from the table."""
        selected = self.vendorNameTable.selectionModel().selectedRows()
        for model_idx in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.vendorNameTable.removeRow(model_idx.row())

    def save_vendor_names(self):
        """Write the current table contents back to the database."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM vendor_names")
        for r in range(self.vendorNameTable.rowCount()):
            metrc = self.vendorNameTable.item(r, 0).text()
            dutchie = self.vendorNameTable.item(r, 1).text()
            cur.execute(
                "INSERT OR REPLACE INTO vendor_names(metrc_vendor, dutchie_vendor) VALUES (?, ?)",
                (metrc, dutchie),
            )
        self.conn.commit()
        QMessageBox.information(
            self, "Saved", f"{self.vendorNameTable.rowCount()} mappings saved."
        )

