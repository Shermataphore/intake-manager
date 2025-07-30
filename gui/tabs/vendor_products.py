# ── intake-manager/gui/tabs/vendor_products.py ───────────────────────
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QFrame, QMessageBox
from PyQt5.QtCore import Qt

class VendorProductsTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()
        # Populate dropdowns when tab loads
        self.load_vendor_mappings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.metrcVendorCombo = QComboBox()
        form.addRow("METRC Vendor:", self.metrcVendorCombo)
        self.dutchieVendorCombo = QComboBox()
        form.addRow("Dutchie Vendor:", self.dutchieVendorCombo)
        layout.addLayout(form)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        input_form = QFormLayout()
        self.prod_metrc_name_input = QLineEdit()
        self.prod_catalog_name_input = QLineEdit()
        input_form.addRow("METRC Product Name", self.prod_metrc_name_input)
        input_form.addRow("Catalog Name", self.prod_catalog_name_input)
        layout.addLayout(input_form)

        btn_layout = QHBoxLayout()
        self.addProductButton = QPushButton("Add Product")
        self.deleteProductButton = QPushButton("Delete Selection")
        btn_layout.addWidget(self.addProductButton)
        btn_layout.addWidget(self.deleteProductButton)
        layout.addLayout(btn_layout)

        # Connect buttons to handlers
        self.addProductButton.clicked.connect(self.add_vendor_product_row)
        self.deleteProductButton.clicked.connect(self.delete_selected_product)
        self.metrcVendorCombo.currentIndexChanged.connect(self.update_dutchie_vendor)

        self.vendorProductTable = QTableWidget(0, 4)
        self.vendorProductTable.setHorizontalHeaderLabels([
            "METRC Name", "Catalog Name", "Cost", "Retail"
        ])
        self.vendorProductTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorProductTable)

    def load_vendor_mappings(self):
        """Populate vendor combos and cache METRC→Dutchie mapping."""
        self.vendor_map = {}
        self.metrcVendorCombo.clear()
        self.metrcVendorCombo.addItem("Select a Vendor")
        cur = self.conn.cursor()
        for metrc, dutchie in cur.execute(
            "SELECT metrc_vendor, dutchie_vendor FROM metrc_dutchie"
        ):
            self.vendor_map[metrc] = dutchie
            self.metrcVendorCombo.addItem(metrc)

    def update_dutchie_vendor(self):
        """Set Dutchie vendor combo when METRC vendor changes."""
        sel = self.metrcVendorCombo.currentText()
        if sel == "Select a Vendor":
            self.dutchieVendorCombo.setCurrentText("")
        else:
            self.dutchieVendorCombo.setCurrentText(self.vendor_map.get(sel, ""))
        self.load_vendor_products()

    def load_vendor_products(self):
        """Fetch products for the selected Dutchie vendor and display them."""
        vendor = self.dutchieVendorCombo.currentText().strip()
        self.vendorProductTable.setRowCount(0)
        if not vendor:
            return
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT metrc_name, catalog_name, cost, retail
            FROM master_product
            WHERE dutchie_vendor = ?
            """,
            (vendor,),
        )
        for r, row in enumerate(cur.fetchall()):
            self.vendorProductTable.insertRow(r)
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.vendorProductTable.setItem(r, c, item)

    def add_vendor_product_row(self):
        """Insert a new product and refresh the table."""
        metrc_name = self.prod_metrc_name_input.text().strip()
        catalog_name = self.prod_catalog_name_input.text().strip()
        dutchie_vendor = self.dutchieVendorCombo.currentText().strip()
        if not (metrc_name and catalog_name and dutchie_vendor):
            QMessageBox.warning(
                self,
                "Missing Data",
                "Please enter both product names and select a vendor.",
            )
            return

        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO master_product (metrc_name, catalog_name, dutchie_vendor)
            VALUES (?, ?, ?)
            """,
            (metrc_name, catalog_name, dutchie_vendor),
        )
        self.conn.commit()

        self.prod_metrc_name_input.clear()
        self.prod_catalog_name_input.clear()
        self.load_vendor_products()

    def delete_selected_product(self):
        """Delete the highlighted products from DB and table."""
        selected = self.vendorProductTable.selectionModel().selectedRows()
        if not selected:
            return
        cur = self.conn.cursor()
        for model_idx in sorted(selected, key=lambda r: r.row(), reverse=True):
            row = model_idx.row()
            metrc = self.vendorProductTable.item(row, 0).text()
            catalog = self.vendorProductTable.item(row, 1).text()
            cur.execute(
                """
                DELETE FROM master_product
                WHERE metrc_name = ? AND catalog_name = ?
                """,
                (metrc, catalog),
            )
            self.vendorProductTable.removeRow(row)
        self.conn.commit()


