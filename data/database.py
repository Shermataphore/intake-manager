# ── intake-manager/data/database.py ───────────────────────────────────
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Allow overrides via environment variables
DEFAULT_DB_PATH = os.path.join(os.getcwd(), "intake.db")
DB_PATH = os.getenv("INTAKE_DB_PATH", DEFAULT_DB_PATH)
DB_FOLDER = os.path.dirname(DB_PATH)

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrc_dutchie (
        metrc_vendor TEXT PRIMARY KEY,
        dutchie_vendor TEXT
    )""")
    conn.commit()
    return conn
