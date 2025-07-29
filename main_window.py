# gui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from gui.tabs.active_manifest import ActiveManifestTab
from gui.tabs.vendor_products import VendorProductsTab
from gui.tabs.vendor_names import VendorNamesTab
# from gui.tabs.regex_search import RegexSearchTab  # (optional for now)

class ManifestManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manifest Manager")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(ActiveManifestTab(), "Active Manifests")
        self.tabs.addTab(VendorProductsTab(), "Vendor Products")
        self.tabs.addTab(VendorNamesTab(), "Vendor Names")
        # self.tabs.addTab(RegexSearchTab(), "Regex Search")  # Optional
