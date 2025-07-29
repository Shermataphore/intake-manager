# ── intake-manager/gui/main_window.py ────────────────────────────────
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from gui.tabs.active_manifest import ActiveManifestTab
from gui.tabs.vendor_products import VendorProductsTab
from gui.tabs.vendor_names import VendorNamesTab
from data.database import init_db

class ManifestManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conn = init_db()
        self.setWindowTitle("Manifest Manager")
        self.resize(1600, 1200)
        font = QFont("Arial", 10)
        self.setFont(font)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255, 248, 220))
        pal.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(pal)
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()
        self.vendor_products_tab = VendorProductsTab(self.conn)
        self.vendor_names_tab = VendorNamesTab(self.conn)

        tabs.addTab(ActiveManifestTab(self.conn), "Active Manifest")
        tabs.addTab(self.vendor_products_tab, "Vendor Products")
        tabs.addTab(self.vendor_names_tab, "Vendor Name Matching")

        self.setCentralWidget(tabs)
