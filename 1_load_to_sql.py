"""
NHANES Project - Step 1
Load all 19 XPT files into MySQL database
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ── YOUR MYSQL DETAILS — FILL THESE IN ───────────────────────────────────────
MYSQL_HOST     = "127.0.0.1"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = quote_plus("VIS@srm3")   # <-- change this to your MySQL password
MYSQL_DATABASE = "nhanes_project"
# ─────────────────────────────────────────────────────────────────────────────

RAW_DATA_DIR = "data/raw"   # folder where your XPT files are

# All 19 XPT files → MySQL table names
XPT_FILES = {
    # Demographics
    "DEMO_L.XPT"   : "demo",

    # Examination
    "BMX_L.XPT"    : "bmx",
    "BPXO_L.XPT"   : "bpxo",

    # Laboratory
    "GHB_L.XPT"    : "ghb",
    "GLU_L.XPT"    : "glu",
    "HDL_L.XPT"    : "hdl",
    "TRIGLY_L.XPT" : "trigly",
    "TCHOL_L.XPT"  : "tchol",
    "INS_L.XPT"    : "ins",
    "HSCRP_L.XPT"  : "hscrp",

    # Questionnaire
    "DIQ_L.XPT"    : "diq",
    "MCQ_L.XPT"    : "mcq",
    "BPQ_L.XPT"    : "bpq",
    "PAQ_L.XPT"    : "paq",
    "SMQ_L.XPT"    : "smq",
    "ALQ_L.XPT"    : "alq",
    "DBQ_L.XPT"    : "dbq",
    "DPQ_L.XPT"    : "dpq",
    "SLQ_L.XPT"    : "slq",
}


def create_db_engine():
    url = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    engine = create_engine(url)
    return engine


def load_xpt_to_mysql():
    print("=" * 55)
    print("  NHANES XPT → MySQL Loader")
    print("=" * 55)

    # Test connection
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"\nConnected to MySQL: {MYSQL_DATABASE}")
    except Exception as e:
        print(f"\n[ERROR] Cannot connect to MySQL: {e}")
        print("Check your password and make sure MySQL is running.")
        return

    print(f"Source folder : {RAW_DATA_DIR}\n")

    success = []
    failed  = []

    for filename, table_name in XPT_FILES.items():
        filepath = os.path.join(RAW_DATA_DIR, filename)

        # Check file exists
        if not os.path.exists(filepath):
            print(f"  [MISSING]  {filename}")
            failed.append(filename)
            continue

        try:
            # Read XPT file
            df = pd.read_sas(filepath, format="xport", encoding="utf-8")

            # Uppercase all column names
            df.columns = df.columns.str.upper()

            # SEQN must exist
            if "SEQN" not in df.columns:
                print(f"  [ERROR]    {filename} — SEQN column not found!")
                failed.append(filename)
                continue

            # Convert SEQN to integer
            df["SEQN"] = df["SEQN"].astype(int)

            # Save to MySQL
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
                chunksize=1000
            )

            rows = len(df)
            cols = len(df.columns)
            print(f"  [OK]  {filename:<22} → '{table_name}' ({rows:,} rows, {cols} cols)")
            success.append(filename)

        except Exception as e:
            print(f"  [ERROR]    {filename} — {e}")
            failed.append(filename)

    print("\n" + "=" * 55)
    print(f"  Done! {len(success)}/{len(XPT_FILES)} files loaded.")
    if failed:
        print(f"\n  Failed files:")
        for f in failed:
            print(f"    - {f}")
    print("=" * 55)
    print("\n  Now go to MySQL Workbench and run:")
    print("    USE nhanes_project;")
    print("    SHOW TABLES;\n")


def verify_tables():
    print("--- MySQL Table Verification ---\n")
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            tables = [r[0] for r in conn.execute(text("SHOW TABLES"))]

        print(f"{'Table':<12} {'Rows':>8}")
        print("-" * 22)
        with engine.connect() as conn:
            for table in sorted(tables):
                count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
                print(f"{table:<12} {count:>8,}")
        print()
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    load_xpt_to_mysql()
    verify_tables()
