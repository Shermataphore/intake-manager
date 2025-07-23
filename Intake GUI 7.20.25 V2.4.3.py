#!/usr/bin/env python3
import sys
import os
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QFormLayout, QLineEdit, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QPushButton, QHBoxLayout, QFrame,
    QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor

# ── Database configuration ─────────────────────────────────────────────────────
DB_FOLDER = r"D:\Scripts\Intake 7.20.25"
DB_PATH = os.path.join(DB_FOLDER, "intake.db")

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Active Manifest Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS active_manifest (
        title TEXT,
        manifest TEXT,
        license TEXT,
        metrc_vendor TEXT,
        received_date TEXT,
        metrc_name TEXT,
        qty REAL,
        cost REAL,
        retail REAL,
        room TEXT,
        strain TEXT
    )""")
    # Master Product Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_product (
        metrc_name TEXT,
        catalog_name TEXT,
        cost REAL,
        retail REAL,
        room TEXT,
        metrc_vendor TEXT,
        dutchie_vendor TEXT,
        category TEXT,
        strain_name TEXT
    )""")
    # METRC ↔ Dutchie Vendor Mapping
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrc_dutchie (
        metrc_vendor TEXT PRIMARY KEY,
        dutchie_vendor TEXT
    )""")
    conn.commit()
    return conn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize DB (creates file + tables if missing)
        self.conn = init_db()

        self.setWindowTitle("Manifest Manager")
        self.resize(1600, 1200)

        # apply theme
        font = QFont("Arial", 10)
        self.setFont(font)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255,248,220))
        pal.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(pal)

        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_overview_tab(), "Active Manifest")
        tabs.addTab(self.create_vendors_tab(), "Vendor Products")
        tabs.addTab(self.create_vendor_name_tab(), "METRC/Dutchie Vendor Name")
        self.setCentralWidget(tabs)

        # load mappings into the METRC→Dutchie combo,
        # which will drive the products table
        self.load_vendor_names()
        self.load_vendor_mappings()

    # ── Active Manifest Tab ──────────────────────────────────────────────────────
    def create_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        self.manifestTitle  = QLineEdit()
        self.manifestNumber = QLineEdit()
        self.vendorLicense  = QLineEdit()
        self.vendorName     = QLineEdit()
        self.receivedDate   = QDateEdit(calendarPopup=True)
        self.receivedDate.setDate(QDate.currentDate())
        form.addRow("Title:",            self.manifestTitle)
        form.addRow("Number:",           self.manifestNumber)
        form.addRow("Vendor License:",   self.vendorLicense)
        form.addRow("Vendor Name:",      self.vendorName)
        form.addRow("Received Date:",    self.receivedDate)
        layout.addLayout(form)

        self.overviewTable = QTableWidget(0,7)
        self.overviewTable.setHorizontalHeaderLabels([
            "Metrc Product Name","Catalog Product Name","Quantity",
            "Cost Per Unit","Retail Price","Room","Strain Name"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)
        return widget

    # ── Vendor Products Tab ──────────────────────────────────────────────────────
    def create_vendors_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # --- top combos ---
        form = QFormLayout()
        self.metrcVendorCombo   = QComboBox(editable=True)
        self.dutchieVendorCombo = QComboBox(editable=True)
        form.addRow("METRC Vendor:",   self.metrcVendorCombo)
        form.addRow("Dutchie Vendor:", self.dutchieVendorCombo)
        layout.addLayout(form)

        # --- separator line ---
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # --- section header ---
        header = QLabel("Add Products")
        header_font = header.font()
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # --- manual‑add form ---
        input_form = QFormLayout()
        self.prod_metrc_name_input   = QLineEdit()
        self.prod_metrc_name_input.setPlaceholderText("METRC Product Name")
        self.prod_catalog_name_input = QLineEdit()
        self.prod_catalog_name_input.setPlaceholderText("Catalog Product Name")
        self.prod_cost_input         = QLineEdit()
        self.prod_cost_input.setPlaceholderText("Cost Per Unit")
        self.prod_rec_price_input    = QLineEdit()
        self.prod_rec_price_input.setPlaceholderText("Retail Price")
        self.prod_room_combo         = QComboBox()
        self.prod_room_combo.addItems(["Sales Floor","Back Room"])

        input_form.addRow("METRC Product Name:",   self.prod_metrc_name_input)
        input_form.addRow("Catalog Product Name:", self.prod_catalog_name_input)
        input_form.addRow("Cost Per Unit:",         self.prod_cost_input)
        input_form.addRow("Retail Price:",          self.prod_rec_price_input)
        input_form.addRow("Room:",                  self.prod_room_combo)

        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(80)
        add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_btn.clicked.connect(self.add_vendor_product_row)
        input_form.addRow("", add_btn)

        layout.addLayout(input_form)

        # --- products table ---
        self.vendorProductTable = QTableWidget(0,6)
        self.vendorProductTable.setHorizontalHeaderLabels([
            "METRC Name","Catalog Name","Cost Per Unit",
            "Retail Price","Room","Dutchie Vendor"
        ])
        self.vendorProductTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorProductTable)

        return widget

    def add_vendor_product_row(self):
        # grab values from the form
        metrc           = self.prod_metrc_name_input.text().strip()
        catalog         = self.prod_catalog_name_input.text().strip()
        cost_str        = self.prod_cost_input.text().strip()
        retail_str      = self.prod_rec_price_input.text().strip()
        room            = self.prod_room_combo.currentText()
        metrc_vendor    = self.metrcVendorCombo.currentText()
        dutchie_vendor  = self.dutchieVendorCombo.currentText()

        # only proceed if at least one field is non‑empty
        if not (metrc or catalog or cost_str or retail_str):
            return

        # 1) Add to the GUI table
        r = self.vendorProductTable.rowCount()
        self.vendorProductTable.insertRow(r)
        for col, val in enumerate([
            metrc, catalog, cost_str, retail_str, room, dutchie_vendor
        ]):
            itm = QTableWidgetItem(val)
            itm.setTextAlignment(Qt.AlignCenter)
            self.vendorProductTable.setItem(r, col, itm)

        # 2) Insert into master_product table in SQLite
        try:
            cost   = float(cost_str)   if cost_str   else 0.0
            retail = float(retail_str) if retail_str else 0.0
        except ValueError:
            cost, retail = 0.0, 0.0

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO master_product
              (metrc_name, catalog_name, cost, retail,
               room, metrc_vendor, dutchie_vendor,
               category, strain_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrc,
            catalog,
            cost,
            retail,
            room,
            metrc_vendor,
            dutchie_vendor,
            "",                # category blank
            "1Unit Item"      # fixed strain_name
        ))
        self.conn.commit()

        # 3) Refresh the product list to show the newly‑added row
        self.load_vendor_products()

        # 4) Clear the inputs
        self.prod_metrc_name_input.clear()
        self.prod_catalog_name_input.clear()
        self.prod_cost_input.clear()
        self.prod_rec_price_input.clear()
        self.prod_room_combo.setCurrentIndex(0)


    def load_vendor_products(self):
        """ Query master_product for current dutchie_vendor and refresh table """
        vendor = self.dutchieVendorCombo.currentText().strip()
        self.vendorProductTable.setRowCount(0)
        if not vendor or vendor == "":
            return

        cur = self.conn.cursor()
        cur.execute("""
            SELECT metrc_name, catalog_name, cost, retail, room, dutchie_vendor
            FROM master_product
            WHERE dutchie_vendor = ?
        """, (vendor,))
        for r, row in enumerate(cur.fetchall()):
            self.vendorProductTable.insertRow(r)
            for c, val in enumerate(row):
                itm = QTableWidgetItem(str(val))
                itm.setTextAlignment(Qt.AlignCenter)
                self.vendorProductTable.setItem(r, c, itm)

    # ── Vendor Name Tab ──────────────────────────────────────────────────────────
    def create_vendor_name_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        inp = QHBoxLayout()
        self.new_metrc_input  = QLineEdit(); self.new_metrc_input.setPlaceholderText("Vendor Name From METRC")
        self.new_dutchie_input= QLineEdit(); self.new_dutchie_input.setPlaceholderText("Vendor Name In Dutchie")
        btn_add = QPushButton("Add"); btn_add.clicked.connect(self.add_vendor_row)
        inp.addWidget(self.new_metrc_input); inp.addWidget(self.new_dutchie_input); inp.addWidget(btn_add)
        layout.addLayout(inp)

        self.vendorNameTable = QTableWidget(0,2)
        self.vendorNameTable.setHorizontalHeaderLabels([
            "Vendor Name From METRC","Vendor Name In Dutchie"
        ])
        self.vendorNameTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorNameTable)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_vendor_names)
        layout.addWidget(btn_save, alignment=Qt.AlignRight)

        return widget

    def add_vendor_row(self):
        m = self.new_metrc_input.text().strip()
        d = self.new_dutchie_input.text().strip()
        if m or d:
            r = self.vendorNameTable.rowCount()
            self.vendorNameTable.insertRow(r)
            itm_m = QTableWidgetItem(m); itm_m.setTextAlignment(Qt.AlignCenter)
            itm_d = QTableWidgetItem(d); itm_d.setTextAlignment(Qt.AlignCenter)
            self.vendorNameTable.setItem(r,0,itm_m)
            self.vendorNameTable.setItem(r,1,itm_d)
            self.new_metrc_input.clear(); self.new_dutchie_input.clear()

    def save_vendor_names(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM metrc_dutchie")
        for r in range(self.vendorNameTable.rowCount()):
            metrc   = self.vendorNameTable.item(r,0).text()
            dutchie = self.vendorNameTable.item(r,1).text()
            cur.execute(
                "INSERT OR REPLACE INTO metrc_dutchie(metrc_vendor,dutchie_vendor) VALUES(?,?)",
                (metrc,dutchie)
            )
        self.conn.commit()
        QMessageBox.information(self, "Saved", f"{self.vendorNameTable.rowCount()} mappings saved.")
        self.load_vendor_mappings()

    def load_vendor_names(self):
        # populate the table in the Name‑mapping tab
        self.vendorNameTable.setRowCount(0)
        cur = self.conn.cursor()
        for metrc, dutchie in cur.execute("SELECT metrc_vendor,dutchie_vendor FROM metrc_dutchie"):
            r = self.vendorNameTable.rowCount()
            self.vendorNameTable.insertRow(r)
            itm_m = QTableWidgetItem(metrc); itm_m.setTextAlignment(Qt.AlignCenter)
            itm_d = QTableWidgetItem(dutchie); itm_d.setTextAlignment(Qt.AlignCenter)
            self.vendorNameTable.setItem(r,0,itm_m)
            self.vendorNameTable.setItem(r,1,itm_d)

    def load_vendor_mappings(self):
        # fill the top comboboxes on the Vendor Products tab
        self.vendor_map = {}
        self.metrcVendorCombo.clear()
        self.metrcVendorCombo.addItem("Select a Vendor")
        cur = self.conn.cursor()
        for metrc, dutchie in cur.execute("SELECT metrc_vendor,dutchie_vendor FROM metrc_dutchie"):
            self.vendor_map[metrc] = dutchie
            self.metrcVendorCombo.addItem(metrc)

        # when user picks a METRC vendor, we set the Dutchie combo + reload products
        self.metrcVendorCombo.currentIndexChanged.connect(self.update_dutchie_vendor)

    def update_dutchie_vendor(self, idx):
        sel = self.metrcVendorCombo.currentText()
        if sel == "Select a Vendor":
            self.dutchieVendorCombo.setCurrentText("")
        else:
            self.dutchieVendorCombo.setCurrentText(self.vendor_map.get(sel, ""))
        # now refresh the products table
        self.load_vendor_products()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
