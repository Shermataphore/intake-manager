# ── intake-manager/main.py ─────────────────────────────────────────────
from gui.main_window import ManifestManagerApp
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManifestManagerApp()
    window.show()
    sys.exit(app.exec_())
