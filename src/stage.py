import sqlite3, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "stores.db"
COLS = {0: "store_id", 1: "name", 2: "branch", 4: "category_large", 6: "category_mid",
        8: "category_small", 13: "sigungu_code", 14: "sigungu_name",
        16: "admin_dong", 31: "road_address", 37: "longitude", 38: "latitude"}
SCHEMA = """CREATE TABLE IF NOT EXISTS stores (
    store_id TEXT,
    name TEXT,
    branch TEXT,
    category_large TEXT,
    category_mid TEXT,
    category_small TEXT,
    sigungu_code TEXT,
    sigungu_name TEXT,
    admin_dong TEXT,
    road_address TEXT,
    longitude REAL,
    latitude REAL,
    city TEXT, 
    district TEXT,
    snapshot TEXT,
    PRIMARY KEY (store_id, snapshot)
)"""
def stage(raw_csv, db=DB):
    raw_csv = Path(raw_csv)
    if not raw_csv.exists():
        raise FileNotFoundError(f"Raw CSV file not found: {raw_csv}")
    snapshot = raw_csv.stem.split("_")[-1]
    df = pd.read_csv(raw_csv, usecols=COLS.keys(), dtype=str)
    df.columns = [COLS[i] for i in sorted(COLS)]
    df[["city","district"]] = df["sigungu_name"].str.split(" ", n=1, expand=True)
    df = df.drop(columns=["sigungu_name"])
    for col in ["longitude", "latitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["snapshot"] = snapshot
    with sqlite3.connect(db) as con:
        con.execute(SCHEMA)
        con.execute("DELETE FROM stores WHERE snapshot = ?", (snapshot,))
        df.to_sql("stores", con, if_exists="append", index=False)
    return len(df)

if __name__ == "__main__":
    print(stage(sys.argv[1]))