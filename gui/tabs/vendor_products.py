# ── intake-manager/gui/tabs/vendor_products.py ───────────────────────
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QEvent

class VendorProductsTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()
        self.load_vendor_mappings()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Vendor selectors
        form = QFormLayout()
        self.metrcVendorCombo = QComboBox()
        form.addRow("METRC Vendor:", self.metrcVendorCombo)
        self.dutchieVendorCombo = QComboBox()
        form.addRow("Dutchie Vendor:", self.dutchieVendorCombo)
        layout.addLayout(form)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # Add product inputs
        input_form = QFormLayout()
        self.prod_metrc_name_input = QLineEdit()
        self.prod_catalog_name_input = QLineEdit()
        input_form.addRow("METRC Product Name", self.prod_metrc_name_input)
        input_form.addRow("Catalog Name", self.prod_catalog_name_input)
        layout.addLayout(input_form)

        # Add/Delete buttons
        btn_layout = QHBoxLayout()
        self.addProductButton = QPushButton("Add Product")
        self.deleteProductButton = QPushButton("Delete Selection")
        btn_layout.addWidget(self.addProductButton)
        btn_layout.addWidget(self.deleteProductButton)
        layout.addLayout(btn_layout)

        # Connect signals
        self.metrcVendorCombo.currentIndexChanged.connect(self.update_dutchie_vendor)
        self.addProductButton.clicked.connect(self.add_vendor_product_row)
        self.deleteProductButton.clicked.connect(self.delete_selected_product)

        # Products table
        self.vendorProductTable = QTableWidget(0, 4)
        self.vendorProductTable.setHorizontalHeaderLabels([
            "METRC Name", "Catalog Name", "Cost", "Retail"
        ])
        self.vendorProductTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorProductTable)

        # Install event filter for paste
        self.vendorProductTable.installEventFilter(self)

        # Save button
        self.saveButton = QPushButton("Save Changes")
        layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.save_product_changes)

    def eventFilter(self, source, event):
        # Capture Ctrl+V on table to paste multiline into METRC Name
        if source == self.vendorProductTable and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
                self.handle_table_paste()
                return True
        return super().eventFilter(source, event)

    def handle_table_paste(self):
        clipboard_text = QApplication.clipboard().text()
        lines = [l for l in clipboard_text.splitlines() if l.strip()]
        if not lines:
            return
        # Determine starting row: current row or 0
        start_row = self.vendorProductTable.currentRow()
        if start_row < 0:
            start_row = 0
        # Paste each line into METRC Name column
        for i, text in enumerate(lines):
            row = start_row + i
            # Ensure row exists
            if row >= self.vendorProductTable.rowCount():
                self.vendorProductTable.insertRow(row)
            item = self.vendorProductTable.item(row, 0)
            if item is None:
                item = QTableWidgetItem()
                self.vendorProductTable.setItem(row, 0, item)
            item.setText(text)

    def load_vendor_mappings(self):
        """Populate METRC combo and clear Dutchie."""
        self.vendor_map = {}
        self.metrcVendorCombo.clear()
        self.metrcVendorCombo.addItem("Select a Vendor")
        cur = self.conn.cursor()
        for metrc, dutchie in cur.execute(
            "SELECT metrc_vendor, dutchie_vendor FROM vendor_names"
        ):
            self.vendor_map[metrc] = dutchie
            self.metrcVendorCombo.addItem(metrc)
        self.dutchieVendorCombo.clear()

    def update_dutchie_vendor(self):
        """When METRC vendor changes, clear table and show its Dutchie mapping."""
        metrc_sel = self.metrcVendorCombo.currentText()
        self.dutchieVendorCombo.clear()
        self.vendorProductTable.setRowCount(0)
        if metrc_sel == "Select a Vendor":
            return
        dutchie = self.vendor_map.get(metrc_sel)
        if dutchie:
            self.dutchieVendorCombo.addItem(dutchie)
            self.dutchieVendorCombo.setCurrentIndex(0)
            self.load_vendor_products()

    def load_vendor_products(self):
        """Load unique catalog entries and make cells editable."""
        vendor = self.dutchieVendorCombo.currentText().strip()
        self.vendorProductTable.setRowCount(0)
        self.original_records = []
        if not vendor:
            return
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT metrc_name, catalog_name, cost, retail
            FROM master_product
            WHERE dutchie_vendor = ?
            GROUP BY catalog_name
            """,
            (vendor,)
        )
        for r, (m, cat, cost, ret) in enumerate(cur.fetchall()):
            self.original_records.append((m, cat))
            self.vendorProductTable.insertRow(r)
            for c, val in enumerate((m, cat, cost, ret)):
                item = QTableWidgetItem("" if val is None else str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if c in (0, 2, 3):
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.vendorProductTable.setItem(r, c, item)

    def add_vendor_product_row(self):
        """Add a new product, preventing duplicate catalog entries."""
        metrc_name = self.prod_metrc_name_input.text().strip()
        catalog_name = self.prod_catalog_name_input.text().strip()
        dutchie_vendor = self.dutchieVendorCombo.currentText().strip()
        if not (metrc_name and catalog_name and dutchie_vendor):
            QMessageBox.warning(self, "Missing Data", "Please enter product and select vendor.")
            return
        cur = self.conn.cursor()
        cur.execute(
            "SELECT COUNT(1) FROM master_product WHERE dutchie_vendor = ? AND catalog_name = ?",
            (dutchie_vendor, catalog_name)
        )
        if cur.fetchone()[0] > 0:
            QMessageBox.information(self, "Duplicate Entry",
                f"Catalog '{catalog_name}' already exists for '{dutchie_vendor}'.")
            return
        cur.execute(
            "INSERT INTO master_product (metrc_name, catalog_name, dutchie_vendor) VALUES (?,?,?)",
            (metrc_name, catalog_name, dutchie_vendor)
        )
        self.conn.commit()
        self.prod_metrc_name_input.clear()
        self.prod_catalog_name_input.clear()
        self.load_vendor_products()

    def delete_selected_product(self):
        """Delete highlighted rows from DB and table."""
        selected = self.vendorProductTable.selectionModel().selectedRows()
        if not selected:
            return
        cur = self.conn.cursor()
        for idx in sorted(selected, key=lambda i: i.row(), reverse=True):
            row = idx.row()
            metrc = self.vendorProductTable.item(row, 0).text()
            catalog = self.vendorProductTable.item(row, 1).text()
            cur.execute(
                "DELETE FROM master_product WHERE metrc_name=? AND catalog_name=?",
                (metrc, catalog)
            )
            self.vendorProductTable.removeRow(row)
        self.conn.commit()

    def save_product_changes(self):
        """Save edited METRC, cost, and retail back to DB."""
        dutchie_vendor = self.dutchieVendorCombo.currentText().strip()
        if not dutchie_vendor:
            QMessageBox.warning(self, "No Vendor", "Select a METRC vendor first.")
            return
        cur = self.conn.cursor()
        for r in range(self.vendorProductTable.rowCount()):
            new_metrc = self.vendorProductTable.item(r, 0).text().strip()
            catalog = self.vendorProductTable.item(r, 1).text().strip()
            cost_text = self.vendorProductTable.item(r, 2).text().strip()
            retail_text = self.vendorProductTable.item(r, 3).text().strip()
            cost = float(cost_text) if cost_text else None
            retail = float(retail_text) if retail_text else None
            orig_metrc, orig_catalog = self.original_records[r]
            cur.execute(
                "UPDATE master_product SET metrc_name=?, cost=?, retail=?"
                " WHERE metrc_name=? AND catalog_name=? AND dutchie_vendor=?",
                (new_metrc, cost, retail, orig_metrc, orig_catalog, dutchie_vendor)
            )
        self.conn.commit()
        QMessageBox.information(self, "Saved", "All changes have been saved.")
