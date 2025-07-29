# main.py
from gui.main_window import ManifestManagerApp

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ManifestManagerApp()
    window.show()
    sys.exit(app.exec_())
