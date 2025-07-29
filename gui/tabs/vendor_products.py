# ── intake-manager/gui/tabs/vendor_products.py ───────────────────────
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QFrame, QMessageBox
from PyQt5.QtCore import Qt

class VendorProductsTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()

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

        self.vendorProductTable = QTableWidget(0, 4)
        self.vendorProductTable.setHorizontalHeaderLabels([
            "METRC Name", "Catalog Name", "Cost", "Retail"
        ])
        self.vendorProductTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorProductTable)
