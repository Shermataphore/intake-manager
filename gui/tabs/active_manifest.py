# ── intake-manager/gui/tabs/active_manifest.py ───────────────────────
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QDate

class ActiveManifestTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.titleInput = QLineEdit()
        form.addRow("Title:", self.titleInput)
        self.manifestInput = QLineEdit()
        form.addRow("Manifest:", self.manifestInput)
        self.licenseInput = QLineEdit()
        form.addRow("License:", self.licenseInput)
        self.metrcVendorInput = QComboBox()
        form.addRow("METRC Vendor:", self.metrcVendorInput)
        self.dateInput = QDateEdit()
        self.dateInput.setCalendarPopup(True)
        self.dateInput.setDate(QDate.currentDate())
        form.addRow("Received Date:", self.dateInput)
        layout.addLayout(form)

        self.overviewTable = QTableWidget(0, 11)
        self.overviewTable.setHorizontalHeaderLabels([
            "Title", "Manifest", "License", "METRC Vendor", "Received Date",
            "METRC Name", "Qty", "Cost", "Retail", "Room", "Strain"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)
