# ── intake-manager/gui/tabs/active_manifest.py ───────────────────────
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import QDate

class ActiveManifestTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)



        # --- top form inputs ---
        form = QFormLayout()
        self.titleCombo = QComboBox()
        form.addRow("Transaction Title:", self.titleCombo)
        self.manifestInput = QLineEdit()
        form.addRow("Manifest:", self.manifestInput)
        self.licenseInput = QLineEdit()
        form.addRow("License:", self.licenseInput)
        self.metrcVendorInput = QComboBox()
        form.addRow("METRC Vendor:", self.metrcVendorInput)
        self.dateInput = QDateEdit(calendarPopup=True)
        self.dateInput.setDate(QDate.currentDate())
        form.addRow("Received Date:", self.dateInput)
        layout.addLayout(form)



        # --- button row (Retrieve … left, Load … right) ---
        btnLayout = QHBoxLayout()
        self.retrieveButton = QPushButton("Scrape Manifests from Dutchie")
        btnLayout.addWidget(self.retrieveButton)
        btnLayout.addStretch()
        self.loadButton = QPushButton("Load Manifest into table")
        btnLayout.addWidget(self.loadButton)
        layout.addLayout(btnLayout)

        # --- overview table ---
        self.overviewTable = QTableWidget(0, 11)
        self.overviewTable.setHorizontalHeaderLabels([
            "Title", "Manifest", "License", "METRC Vendor", "Received Date",
            "METRC Name", "Qty", "Cost", "Retail", "Room", "Strain"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)
