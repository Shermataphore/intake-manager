# intake-manager/gui/tabs/active_manifest.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from automation.receive_inventory import scrape_receive_inventory


class InventoryScrapeWorker(QObject):
    """Worker object that scrapes inventory data in a background thread."""

    # Emits the scraped data once complete
    resultsReady = pyqtSignal(dict)

    def run(self):
        """Execute the scraping task and emit the results."""
        try:
            data = scrape_receive_inventory()
        except Exception as exc:  # pragma: no cover - debug aid
            # Errors are printed so that the UI thread is not blocked
            print("Error scraping:", exc)
            data = {}
        self.resultsReady.emit(data)

class ActiveManifestTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.scraped_results = {}
        self._scrape_thread = None
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

        # License input. Dutchie does not expose this directly when scraping so
        # we keep it as a free-form field for now.  It was previously commented
        # out which caused an AttributeError when populating the table.
        self.licenseInput = QLineEdit()
        form.addRow("License:", self.licenseInput)

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
        """Spawn a worker thread to scrape inventory data."""
        self.retrieveButton.setEnabled(False)

        worker = InventoryScrapeWorker()
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.resultsReady.connect(self.handle_scrape_results)
        worker.resultsReady.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda: self.retrieveButton.setEnabled(True))
        thread.start()

        # keep a reference to avoid garbage collection
        self._scrape_thread = thread

    def handle_scrape_results(self, results):
        """Receive scraped data on the main thread and update the UI."""
        self.scraped_results = results
        self.titleCombo.clear()
        self.titleCombo.addItems(results.keys())
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

        # Automatically refresh the table when a new transaction is selected
        self.on_load()

    def on_load(self):
        title = self.titleCombo.currentText()
        items = self.scraped_results.get(title, [])

        self.overviewTable.setRowCount(len(items))
        for row, itm in enumerate(items):
            self.overviewTable.setItem(row, 0, QTableWidgetItem(title))
            self.overviewTable.setItem(row, 1, QTableWidgetItem(self.manifestInput.text()))
            # licenseInput is a QLineEdit; grab its text directly
            self.overviewTable.setItem(row, 2, QTableWidgetItem(self.licenseInput.text()))
            self.overviewTable.setItem(row, 3, QTableWidgetItem(self.metrcVendorInput.text()))
            self.overviewTable.setItem(row, 4, QTableWidgetItem(self.dateInput.text()))
            self.overviewTable.setItem(row, 5, QTableWidgetItem(itm.get("name", "")))
            qty = itm.get("quantity", itm.get("qty", ""))
            self.overviewTable.setItem(row, 6, QTableWidgetItem(qty))
            self.overviewTable.setItem(row, 7, QTableWidgetItem(itm.get("cost", "")))
            self.overviewTable.setItem(row, 8, QTableWidgetItem(itm.get("retail", "")))
            self.overviewTable.setItem(row, 9, QTableWidgetItem(""))
            self.overviewTable.setItem(row, 10, QTableWidgetItem(""))
