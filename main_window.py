# ── intake-manager/gui/main_window.py ────────────────────────────────
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from gui.tabs.active_manifest import ActiveManifestTab
from gui.tabs.vendor_products import VendorProductsTab
from gui.tabs.vendor_names import VendorNamesTab
from gui.tabs.regex_search import RegexProWithSaveTab
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
        tabs.addTab(ActiveManifestTab(self.conn), "Active Manifest")
        tabs.addTab(VendorProductsTab(self.conn), "Vendor Products")
        tabs.addTab(VendorNamesTab(self.conn), "Vendor Name Matching")
        self.regex_tab = RegexProWithSaveTab()
        tabs.addTab(self.regex_tab, "Vendor Regex Config")
        self.setCentralWidget(tabs)

        tabs.widget(2).set_regex_tab(self.regex_tab)
