# intake-manager/gui/tabs/active_manifest.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from automation.receive_inventory import scrape_receive_inventory

class ActiveManifestTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.scraped_results = {}
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.titleCombo = QComboBox()
        form.addRow("Transaction Title:", self.titleCombo)

        # Manifest as free-form input
        self.manifestInput = QLineEdit()
        form.addRow("Manifest:", self.manifestInput)

        # METRC Vendor as free-form input
        self.metrcVendorInput = QLineEdit()
        form.addRow("METRC Vendor:", self.metrcVendorInput)

        # Received Date as free-form input
        self.dateInput = QLineEdit()
        self.dateInput.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Received Date:", self.dateInput)

        layout.addLayout(form)

        btnLayout = QHBoxLayout()
        self.retrieveButton = QPushButton("Scrape Manifests from Dutchie")
        btnLayout.addWidget(self.retrieveButton)
        btnLayout.addStretch()
        self.loadButton = QPushButton("Load Manifest into table")
        btnLayout.addWidget(self.loadButton)
        layout.addLayout(btnLayout)

        self.overviewTable = QTableWidget(0, 11)
        self.overviewTable.setHorizontalHeaderLabels([
            "Title", "Manifest", "License", "METRC Vendor", "Received Date",
            "METRC Name", "Qty", "Cost", "Retail", "Room", "Strain"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)

    def _connect_signals(self):
        self.retrieveButton.clicked.connect(self.on_retrieve)
        self.loadButton.clicked.connect(self.on_load)
        self.titleCombo.currentTextChanged.connect(self.on_title_changed)

    def on_retrieve(self):
        try:
            self.scraped_results = scrape_receive_inventory()
        except Exception as e:
            print("Error scraping:", e)
            return

        self.titleCombo.clear()
        self.titleCombo.addItems(self.scraped_results.keys())
        if self.titleCombo.count() > 0:
            self.titleCombo.setCurrentIndex(0)
            self.on_title_changed(self.titleCombo.currentText())

    def on_title_changed(self, title):
        if not title:
            self.dateInput.clear()
            return

        # Manifest = last 8 characters
        self.manifestInput.setText(title[-8:])

        # METRC Vendor = text between first and last hyphens
        first_dash = title.find('-')
        last_dash = title.rfind('-')
        vendor = title[first_dash+1:last_dash] if 0 <= first_dash < last_dash else ''
        self.metrcVendorInput.setText(vendor)

        # Received Date = first 10 characters of title
        date_str = title[:10]
        self.dateInput.setText(date_str)

    def on_load(self):
        title = self.titleCombo.currentText()
        items = self.scraped_results.get(title, [])

        # prepare DB cursor
        cur = self.conn.cursor()

        # set row count
        self.overviewTable.setRowCount(len(items))
        for row, itm in enumerate(items):
            metrc_name = itm.get("name", "")
            qty = itm.get("qty", "")

            # Lookup in master_product by metrc_name
            cur.execute(
                "SELECT catalog_name, cost, retail, room, strain_name FROM master_product WHERE metrc_name = ?",
                (metrc_name,)
            )
            prod = cur.fetchone()
            if prod:
                catalog_name, cost, retail, room, strain = prod
            else:
                # fallback defaults
                catalog_name = metrc_name
                cost = ''
                retail = ''
                room = "Back Room" if "Sample" in metrc_name else "Sales Floor"
                strain = "1Unit Item"

            # Populate columns according to ActiveManifest Notes:
            # Title = catalog product name
            self.overviewTable.setItem(row, 0, QTableWidgetItem(catalog_name))
            # Manifest, License blank, METRC Vendor, Received Date
            self.overviewTable.setItem(row, 1, QTableWidgetItem(self.manifestInput.text()))
            self.overviewTable.setItem(row, 2, QTableWidgetItem(""))
            self.overviewTable.setItem(row, 3, QTableWidgetItem(self.metrcVendorInput.text()))
            self.overviewTable.setItem(row, 4, QTableWidgetItem(self.dateInput.text()))
            # METRC Name, Qty
            self.overviewTable.setItem(row, 5, QTableWidgetItem(metrc_name))
            self.overviewTable.setItem(row, 6, QTableWidgetItem(qty))
            # Cost, Retail, Room, Strain
            self.overviewTable.setItem(row, 7, QTableWidgetItem(str(cost)))
            self.overviewTable.setItem(row, 8, QTableWidgetItem(str(retail)))
            self.overviewTable.setItem(row, 9, QTableWidgetItem(room))
            self.overviewTable.setItem(row, 10, QTableWidgetItem(strain))
