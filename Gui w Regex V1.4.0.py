#!/usr/bin/env python3
import sys
import os
import re
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QFormLayout, QLineEdit, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QPushButton, QFrame,
    QMessageBox, QSizePolicy, QLabel, QCheckBox, QSpinBox
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

# ── Regex Extraction Classes ───────────────────────────────────────────────────
class ExtractionField:
    MODES = ["Regex", "Split", "Prefix", "Suffix", "Full Regex"]

    def __init__(self, name: str, parent_layout: QVBoxLayout, update_callback):
        # Enable toggle
        self.checkbox = QCheckBox()
        # Mode selector
        self.mode = QComboBox()
        self.mode.addItems(self.MODES)
     
        # Regex inputs
        self.before  = QLineEdit(); self.before .setPlaceholderText("Before")
        self.after   = QLineEdit(); self.after  .setPlaceholderText("After")
        
        # Split inputs
        self.delim   = QLineEdit(); self.delim  .setPlaceholderText("Delimiter")
        self.delim.setText(" - ")
        self.index   = QSpinBox(); self.index  .setRange(1, 50)
        
        # Prefix/Suffix input
        self.anchor  = QLineEdit(); self.anchor .setPlaceholderText("Text")
        
        # Full-regex input
        self.pattern = QLineEdit(); self.pattern.setPlaceholderText(r"Regex with (one) group")

        # Result display
        self.result  = QLabel(); self.result.setMinimumWidth(200)

        # Build UI row
        row = QHBoxLayout()
        row.addWidget(self.checkbox)
        row.addWidget(QLabel(f"{name}:"))
        row.addWidget(self.mode)
        row.addWidget(self.before)
        row.addWidget(self.after)
        row.addWidget(self.delim)
        row.addWidget(self.index)
        row.addWidget(self.anchor)
        row.addWidget(self.pattern)
        row.addWidget(QLabel("→"))
        row.addWidget(self.result)
        parent_layout.addLayout(row)

        # Pattern preview row
        self.pattern_label = QLabel()
        self.pattern_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pat_row = QHBoxLayout()
        pat_row.addSpacing(30)
        pat_row.addWidget(QLabel("Regex:"))
        pat_row.addWidget(self.pattern_label)
        parent_layout.addLayout(pat_row)

        # Initial widget state
        self._toggle_widgets()
        
        # Connect signals
        self.checkbox.stateChanged.connect(update_callback)
        self.mode.currentIndexChanged.connect(lambda _: (self._toggle_widgets(), update_callback()))
        self.before.textChanged.connect(update_callback)
        self.after.textChanged.connect(update_callback)
        self.delim.textChanged.connect(update_callback)
        self.index.valueChanged.connect(update_callback)
        self.anchor.textChanged.connect(update_callback)
        self.pattern.textChanged.connect(update_callback)

    def _toggle_widgets(self):
        m = self.mode.currentText()
        self.before .setVisible(m == "Regex")
        self.after  .setVisible(m == "Regex")
        self.delim  .setVisible(m == "Split")
        self.index  .setVisible(m == "Split")
        self.anchor .setVisible(m in ("Prefix", "Suffix"))
        self.pattern.setVisible(m == "Full Regex")

    def compute_pattern(self):
        mode = self.mode.currentText()
        if mode == "Regex":
            b, a = self.before.text(), self.after.text()
            return re.escape(b) + r"(.*?)" + re.escape(a)
        elif mode == "Split":
            d = self.delim.text(); idx = self.index.value() - 1
            return (r"^(?:.*?" + re.escape(d) + r"){" + str(idx) + r"}" + r"(.*?)" +
                    r"(?:(?:" + re.escape(d) + r")|$)")
        elif mode == "Prefix": return re.escape(self.anchor.text()) + r"(.*)"
        elif mode == "Suffix": return r"(.*?)" + re.escape(self.anchor.text())
        else: return self.pattern.text()

    def extract(self, text: str):
        if not self.checkbox.isChecked():
            self.pattern_label.setText(""); return ""
        pat = self.compute_pattern(); self.pattern_label.setText(pat)
        try:
            m = re.search(pat, text)
            return m.group(1) if m else ""
        except re.error:
            self.pattern_label.setText(f"<invalid: {pat}>"); return ""

class RegexProWithSaveTab(QWidget):
    def __init__(self): super().__init__(); self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(5, 5, 5, 5)
        # reduce the space between each item in the vertical stack
        layout.setSpacing(5)
        
        # Vendor selector
        vend = QHBoxLayout()
        vend.setSpacing(5)
        vend.addWidget(QLabel("Vendor:"))
        self.vendor_dropdown = QComboBox()
        vend.addWidget(self.vendor_dropdown)
        layout.addLayout(vend)

        # ── Subcategory selector ────────────────────────────────────────────
        sc_layout = QHBoxLayout()
        sc_layout.setSpacing(5)

        # checkbox to enable/disable
        self.subcategory_checkbox = QCheckBox()
        sc_layout.addWidget(self.subcategory_checkbox)

        sc_layout.addWidget(QLabel("Subcategory:"))
        self.subcategory_dropdown = QComboBox()
        self.subcategory_dropdown.addItem("Select a Subcategory")
        self.subcategory_dropdown.addItems([
            "Beverages",
            "Cannabis Flower",
            "Cartridges / Pens",
            "Concentrate",
            "Edible",
            "Extract",
            "Flower",
            "Hemp Based Products",
            "Hemp CBD Flower",
            "Infused Non-edible",
            "Infused Pre-Roll",
            "Inhalable Cannabis Product - Combined",
            "Marijuana Pre-Roll",
            "Paraphernalia",
            "Pre-Rolls",
            "Seeds",
            "Tobacco Category",
            "Topical",
        ])
        sc_layout.addWidget(self.subcategory_dropdown)

        layout.addLayout(sc_layout)

        # re-connect so the filename updates whenever subcategory changes
        self.subcategory_checkbox.stateChanged.connect(self.update_final_location)
        self.subcategory_dropdown.currentIndexChanged.connect(self.update_final_location)
        # ────────────────────────────────────────────────────────────────────

        
        # Test string
        f = QFormLayout();
        f.setVerticalSpacing(5)       # less space between form rows
        f.setSpacing(5)
        self.test_input = QLineEdit();
        f.addRow("Parse String:", self.test_input);
        layout.addLayout(f)
        
        # Extraction fields
        self.fields=[]
        for name in ("Product Name","Vendor Name","Category"):
            fld=ExtractionField(name,layout,self.update_results);
            # tighten each field’s own rows:
            fld_row = fld.checkbox.parentWidget().layout()      # the HBoxLayout for that row
            fld_row.setSpacing(3)
            fld_row.setContentsMargins(0, 0, 0, 0)
            self.fields.append(fld)

            
            
        # Save path
        s=QHBoxLayout();
        s.setSpacing(5);
        s.setContentsMargins(0, 0, 0, 0);
        s.addWidget(QLabel("Save to location:"));
        self.save_location_input=QLineEdit();
        s.addWidget(self.save_location_input);
        layout.addLayout(s)

        # Final path
        f2=QHBoxLayout();
        f2.setSpacing(5);
        f2.setContentsMargins(0, 0, 0, 0);
        f2.addWidget(QLabel("Final Location:"));
        self.final_location_display=QLineEdit();
        self.final_location_display.setReadOnly(True);
        f2.addWidget(self.final_location_display);
        layout.addLayout(f2)
        
        # Save button
        self.save_button=QPushButton("Save"); layout.addWidget(self.save_button)
        
        # Connect
        self.test_input.textChanged.connect(self.update_results)
        self.vendor_dropdown.currentIndexChanged.connect(self.update_final_location)
        self.save_location_input.textChanged.connect(self.update_final_location)
        self.save_button.clicked.connect(self.save_to_file)
        self.update_final_location()

        # Populate dropdown now that mappings exist
        self.load_vendors()


    def load_vendors(self):
        """
        Populate vendor_dropdown from the metrc_dutchie → dutchie_vendor mapping.
        """
        # DB_PATH is defined at the top of this file
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT dutchie_vendor FROM metrc_dutchie ORDER BY dutchie_vendor")
        rows = [row[0] for row in cur.fetchall()]
        conn.close()

        self.vendor_dropdown.clear()
        self.vendor_dropdown.addItem("Select a Vendor")
        for dut in rows:
            self.vendor_dropdown.addItem(dut)


        
    def update_results(self):
        txt=self.test_input.text()
        for fld in self.fields: fld.result.setText(fld.extract(txt))
        
    def update_final_location(self):
        base   = self.save_location_input.text().strip()
        vendor = self.vendor_dropdown.currentText()

        # only append if checked *and* a real subcategory is chosen
        sc_text = ""
        if (self.subcategory_checkbox.isChecked()
            and self.subcategory_dropdown.currentText() not in ("", "Select a Subcategory")):
            sc_text = " " + self.subcategory_dropdown.currentText()

        if base and vendor != "Select a Vendor":
            folder   = base.rstrip(os.sep)
            filename = f"{vendor}{sc_text}.py"
            final    = os.path.join(folder, filename)
        else:
            final = ""
        self.final_location_display.setText(final)


        
        
    def save_to_file(self):
        path=self.final_location_display.text()
        if not path:
            QMessageBox.warning(self,"Missing info","Please select a vendor and enter a save location."); return
        self.update_results()
        pats={
            "PRODUCT_NAME_PATTERN":self.fields[0].pattern_label.text(),
            "VENDOR_NAME_PATTERN": self.fields[1].pattern_label.text(),
            "CATEGORY_PATTERN": self.fields[2].pattern_label.text()
        }
        content=["import re","",
            f"# Auto-generated parsing script for vendor: {self.vendor_dropdown.currentText()!r}"
        ]
        for k,v in pats.items(): content.append(f"{k} = {repr(v)}")
        content+=["","def parse_string(s):","    results = {}",
            "    m = re.search(PRODUCT_NAME_PATTERN, s)",
            "    results['product_name'] = m.group(1) if m else ''",
            "    m = re.search(VENDOR_NAME_PATTERN, s)",
            "    results['vendor_name']  = m.group(1) if m else ''",
            "    m = re.search(CATEGORY_PATTERN, s)",
            "    results['category']     = m.group(1) if m else ''",
            "    return results",""
        ]
        script="\n".join(content)
        try:
            os.makedirs(os.path.dirname(path),exist_ok=True)
            with open(path,"w",encoding="utf-8") as f: f.write(script)
        except Exception as e:
            QMessageBox.critical(self,"Error Saving",str(e)); return
        QMessageBox.information(self,"Saved",f"Parsing script written to:\n{path}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conn = init_db()
        self.setWindowTitle("Manifest Manager")
        self.resize(1600,1200)
        # Theme
        font = QFont("Arial",10); self.setFont(font)
        pal = QPalette(); pal.setColor(QPalette.Window,QColor(255,248,220));
        pal.setColor(QPalette.WindowText,Qt.black); self.setPalette(pal)
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_overview_tab(),"Active Manifest")
        tabs.addTab(self.create_vendors_tab(),"Vendor Products")
        tabs.addTab(self.create_vendor_name_tab(),"Vendor Name Matching")
        self.regex_tab = RegexProWithSaveTab()
        tabs.addTab(self.regex_tab,"Vendor Regex Config")
        self.setCentralWidget(tabs)
        self.load_vendor_names()
        self.load_vendor_mappings()

    def create_overview_tab(self):
        widget = QWidget(); layout = QVBoxLayout(widget)
        form = QFormLayout()
        # title, manifest, license, etc inputs
        self.titleInput = QLineEdit(); form.addRow("Title:",self.titleInput)
        self.manifestInput = QLineEdit(); form.addRow("Manifest:",self.manifestInput)
        self.licenseInput = QLineEdit(); form.addRow("License:",self.licenseInput)
        self.metrcVendorInput = QComboBox(); form.addRow("METRC Vendor:",self.metrcVendorInput)
        self.dateInput = QDateEdit(); self.dateInput.setCalendarPopup(True); self.dateInput.setDate(QDate.currentDate())
        form.addRow("Received Date:",self.dateInput)
        layout.addLayout(form)
        # table
        self.overviewTable = QTableWidget(0,11)
        self.overviewTable.setHorizontalHeaderLabels([
            "Title","Manifest","License","METRC Vendor","Received Date",
            "METRC Name","Qty","Cost","Retail","Room","Strain"
        ])
        self.overviewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.overviewTable)
        return widget

    def create_vendors_tab(self):
        widget = QWidget(); layout = QVBoxLayout(widget)
        # --- top combos ---
        form = QFormLayout()
        self.metrcVendorCombo  = QComboBox(editable=True)
        form.addRow("METRC Vendor:", self.metrcVendorCombo)
        self.dutchieVendorCombo = QComboBox(editable=True)
        form.addRow("Dutchie Vendor:", self.dutchieVendorCombo)
        layout.addLayout(form)
        
        # separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # manual-add form
        input_form = QFormLayout()
        self.prod_metrc_name_input   = QLineEdit()
        self.prod_metrc_name_input.setPlaceholderText("METRC Product Name")
        self.prod_catalog_name_input = QLineEdit()
        self.prod_catalog_name_input.setPlaceholderText("Catalog Name")
        input_form.addRow("METRC Product Name", self.prod_metrc_name_input)
        input_form.addRow("Catalog Name",      self.prod_catalog_name_input)
        layout.addLayout(input_form)

        # ── INSERT BUTTONS HERE ───────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        # 1) Add Product button
        self.addProductButton = QPushButton("Add Product")
        btn_layout.addWidget(self.addProductButton)
        # 2) Delete Selection button
        self.deleteProductButton = QPushButton("Delete Selection")
        btn_layout.addWidget(self.deleteProductButton)
        layout.addLayout(btn_layout)

        # wire signals on those buttons:
        self.addProductButton.clicked.connect(self.add_vendor_product_row)
        self.deleteProductButton.clicked.connect(self.delete_selected_product)
        # ──────────────────────────────────────────────────────────────────────────

        # table
        self.vendorProductTable = QTableWidget(0,4)
        self.vendorProductTable.setHorizontalHeaderLabels([
            "METRC Name","Catalog Name","Cost","Retail"
        ])
        self.vendorProductTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorProductTable)
        return widget


    def create_vendor_name_tab(self):
        widget=QWidget(); layout=QVBoxLayout(widget)
        # Input fields for new mapping
        new_layout = QHBoxLayout()
        self.new_metrc_input = QLineEdit()
        self.new_metrc_input.setPlaceholderText("New METRC Vendor")
        self.new_dutchie_input = QLineEdit()
        self.new_dutchie_input.setPlaceholderText("New Dutchie Vendor")
        new_layout.addWidget(self.new_metrc_input)
        new_layout.addWidget(self.new_dutchie_input)
        layout.addLayout(new_layout)
                
        # Add & Remove buttons
        btn_layout=QHBoxLayout()
        btn_add=QPushButton("Add Mapping"); btn_add.clicked.connect(self.add_vendor_mapping)
        btn_remove=QPushButton("Remove Selected"); btn_remove.clicked.connect(self.remove_selected_mappings)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_remove); layout.addLayout(btn_layout)
        # Table
        self.vendorNameTable=QTableWidget(0,2)
        self.vendorNameTable.setHorizontalHeaderLabels(["METRC Vendor","Dutchie Vendor"]);
        self.vendorNameTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vendorNameTable)
        # Save Mappings
        btn_save=QPushButton("Save Mappings"); btn_save.clicked.connect(self.save_vendor_names)
        layout.addWidget(btn_save,alignment=Qt.AlignRight)
        return widget

    def add_vendor_mapping(self):
        metrc = self.new_metrc_input.text().strip()
        dutchie = self.new_dutchie_input.text().strip()
        # ensure both inputs are provided
        if not metrc or not dutchie:
            QMessageBox.warning(self, "Missing input", "Please enter both METRC and Dutchie names.")
            return
        # insert the new mapping into the table
        r = self.vendorNameTable.rowCount()
        self.vendorNameTable.insertRow(r)
        item_m = QTableWidgetItem(metrc)
        item_m.setTextAlignment(Qt.AlignCenter)
        self.vendorNameTable.setItem(r, 0, item_m)
        item_d = QTableWidgetItem(dutchie)
        item_d.setTextAlignment(Qt.AlignCenter)
        self.vendorNameTable.setItem(r, 1, item_d)
        # clear input fields for next entry
        self.new_metrc_input.clear()
        self.new_dutchie_input.clear()

    def remove_selected_mappings(self):
        sels = self.vendorNameTable.selectionModel().selectedRows()
        for idx in sorted(sels, key=lambda x: x.row(), reverse=True):
            self.vendorNameTable.removeRow(idx.row())


    def load_vendor_names(self):
        self.vendorNameTable.setRowCount(0)
        cur = self.conn.cursor()
        for r,(metrc,dutchie) in enumerate(cur.execute("SELECT metrc_vendor,dutchie_vendor FROM metrc_dutchie")):
            self.vendorNameTable.insertRow(r)
            itm_m = QTableWidgetItem(metrc); itm_m.setTextAlignment(Qt.AlignCenter)
            itm_d = QTableWidgetItem(dutchie); itm_d.setTextAlignment(Qt.AlignCenter)
            self.vendorNameTable.setItem(r,0,itm_m)
            self.vendorNameTable.setItem(r,1,itm_d)

    def load_vendor_mappings(self):
        self.vendor_map = {}
        self.metrcVendorCombo.clear();
        self.metrcVendorCombo.addItem("Select a Vendor")
        cur = self.conn.cursor()
        for metrc,dutchie in cur.execute(
            "SELECT metrc_vendor,dutchie_vendor FROM metrc_dutchie"
        ):
            self.vendor_map[metrc] = dutchie
            self.metrcVendorCombo.addItem(metrc)
        self.metrcVendorCombo.currentIndexChanged.connect(self.update_dutchie_vendor)
        # The above section was correct to load mapping
        

    def update_dutchie_vendor(self, idx):
        sel = self.metrcVendorCombo.currentText()
        if sel == "Select a Vendor":
            self.dutchieVendorCombo.setCurrentText("")
        else:
            dut = self.vendor_map.get(sel,"")
            self.dutchieVendorCombo.setCurrentText(dut)
        # now refresh the products table
        self.load_vendor_products()   # This was missing

    def load_vendor_products(self):
        """ Query master_product for current dutchie_vendor and refresh table """
        vendor = self.dutchieVendorCombo.currentText().strip()
        self.vendorProductTable.setRowCount(0)
        if not vendor:
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

    def add_vendor_product_row(self):
        """
        Grab the two input fields + current vendor,
        insert into master_product, then reload table.
        """
        metrc_name   = self.prod_metrc_name_input.text().strip()
        catalog_name = self.prod_catalog_name_input.text().strip()
        dutchie_vendor = self.dutchieVendorCombo.currentText().strip()
        if not (metrc_name and catalog_name and dutchie_vendor):
            QMessageBox.warning(self, "Missing Data",
                                "Please enter both product names and select a vendor.")
            return

        # insert into DB
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO master_product
                (metrc_name, catalog_name, dutchie_vendor)
            VALUES (?, ?, ?)
        """, (metrc_name, catalog_name, dutchie_vendor))
        self.conn.commit()

        # clear inputs and refresh
        self.prod_metrc_name_input.clear()
        self.prod_catalog_name_input.clear()
        self.load_vendor_products()


    def delete_selected_product(self):
        """
        Remove highlighted rows from master_product and table.
        """
        sels = self.vendorProductTable.selectionModel().selectedRows()
        if not sels:
            return

        cur = self.conn.cursor()
        # delete DB rows in reverse index order to avoid shifting
        for model_idx in sorted(sels, key=lambda r: r.row(), reverse=True):
            row = model_idx.row()
            metrc = self.vendorProductTable.item(row, 0).text()
            catalog = self.vendorProductTable.item(row, 1).text()
            # delete from DB
            cur.execute("""
                DELETE FROM master_product
                 WHERE metrc_name = ? AND catalog_name = ?
            """, (metrc, catalog))
            # remove from table
            self.vendorProductTable.removeRow(row)
        self.conn.commit()


    def save_vendor_names(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM metrc_dutchie")
        for r in range(self.vendorNameTable.rowCount()):
            metrc = self.vendorNameTable.item(r,0).text()
            dutchie = self.vendorNameTable.item(r,1).text()
            cur.execute(
                "INSERT OR REPLACE INTO metrc_dutchie(metrc_vendor,dutchie_vendor) VALUES(?,?)",
                (metrc,dutchie)
            )
        self.conn.commit()
        QMessageBox.information(self,"Saved",f"{self.vendorNameTable.rowCount()} mappings saved.")
        self.load_vendor_mappings()

        # Refresh the Regex-Config vendor list
        self.regex_tab.load_vendors()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
