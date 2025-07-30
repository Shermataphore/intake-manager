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
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import QDate, Qt
from automation.receive_inventory import scrape_receive_inventory

class ActiveManifestTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.manifest_data = {}
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

        # Connect buttons
        self.retrieveButton.clicked.connect(self.scrape_manifests)
        self.loadButton.clicked.connect(self.load_manifest)

        # --- overview table ---
        self.overviewTable = QTableWidget(0, 11)
        self.overviewTable.setHorizontalHeaderLabels([
            "Title", "Manifest", "License", "METRC Vendor", "Received Date",
            "METRC Name", "Qty", "Cost", "Retail", "Room", "Strain"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)

    def scrape_manifests(self):
        """Retrieve manifests from Dutchie and populate the title combo."""
        try:
            data = scrape_receive_inventory()
            if not isinstance(data, dict):
                raise ValueError("No manifest data returned")
            self.manifest_data = data
            self.titleCombo.clear()
            for title in data.keys():
                self.titleCombo.addItem(title)
        except Exception as exc:
            QMessageBox.warning(self, "Scrape Error", str(exc))

    def load_manifest(self):
        """Load selected manifest items into the overview table."""
        title = self.titleCombo.currentText()
        if not title or title not in self.manifest_data:
            QMessageBox.warning(self, "No Manifest", "Please scrape and select a manifest first.")
            return

        items = self.manifest_data[title]
        self.overviewTable.setRowCount(0)

        manifest = self.manifestInput.text().strip()
        license_text = self.licenseInput.text().strip()
        metrc_vendor = self.metrcVendorInput.currentText().strip()
        received = self.dateInput.date().toString("yyyy-MM-dd")

        for r, item in enumerate(items):
            self.overviewTable.insertRow(r)
            values = [
                title,
                manifest,
                license_text,
                metrc_vendor,
                received,
                item.get("name", ""),
                item.get("qty", ""),
                item.get("cost", ""),
                item.get("rec", ""),
                "",
                "",
            ]
            for c, val in enumerate(values):
                itm = QTableWidgetItem(str(val))
                itm.setTextAlignment(Qt.AlignCenter)
                self.overviewTable.setItem(r, c, itm)
