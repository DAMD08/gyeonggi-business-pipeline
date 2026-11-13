import sqlite3
from datetime import date
import pytest
from src.checks import check_duplicates, check_schema, check_freshness, check_volume, check_nulls, CheckFailed

@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE stores (store_id TEXT, longitude REAL, latitude REAL, snapshot TEXT)")
    c.executemany("INSERT INTO stores VALUES (?,?,?,?)", [(f"a{i}", 127.0, 37.0, "202606") for i in range(100)])
    return c

def test_check_freshness_pass(con):
    today = date(2026, 6, 1)
    check_freshness(con, today)

def test_check_freshness_fail(con):
    today = date(2026, 9, 1)
    with pytest.raises(CheckFailed):
        check_freshness(con, today)

def test_check_volume_pass(con):
    check_volume(con, "202606", 50)
    with pytest.raises(CheckFailed):
        check_volume(con, "202606", 150)

def test_check_nulls_pass(con):
    check_nulls(con, "202606")
    con.execute("UPDATE stores SET longitude = NULL WHERE rowid <= 5")
    with pytest.raises(CheckFailed):
        check_nulls(con, "202606")

def test_check_duplicates(tmp_path):
    p = tmp_path / "test.csv"
    p.write_text("id, x\na, 1\nb, 2\n", encoding="utf-8")
    check_duplicates(p, "id")
    p.write_text("id, x\na, 1\na, 2\n", encoding="utf-8")
    with pytest.raises(CheckFailed):
        check_duplicates(p, "id")

def test_check_schema(tmp_path):
    p1 = tmp_path / "test1.csv"
    p2 = tmp_path / "test2.csv"
    p1.write_text("id, x\na, 1\nb, 2\n", encoding="utf-8")
    p2.write_text("id, x\na, 1\nb, 2\n", encoding="utf-8")
    check_schema(p1, p2)
    p2.write_text("id, y\na, 1\nb, 2\n", encoding="utf-8")
    with pytest.raises(CheckFailed):
        check_schema(p1, p2)