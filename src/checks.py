class CheckFailed(Exception):
    pass

def check_freshness(con, today, max_age_months=2):
    """
    Check if the latest snapshot in the database is within the allowed age.
    Raises CheckFailed if the check fails.
    """
    latest = con.execute("SELECT MAX(snapshot) FROM stores").fetchone()[0]
    if latest is None:
        raise CheckFailed("No snapshots found in the database.")
    age = (today.year - int(latest[:4])) * 12 + (today.month - int(latest[4:]))
    if age > max_age_months:
        raise CheckFailed(f"Latest snapshot {latest} is older than {max_age_months} months.")

def check_volume(con, snapshot, min_rows):
    """
    Check if the number of rows for the given snapshot meets the minimum requirement.
    Raises CheckFailed if the check fails.
    """
    n = con.execute("SELECT COUNT(*) FROM stores WHERE snapshot = ?", (snapshot,)).fetchone()[0]
    if n < min_rows:
        raise CheckFailed(f"Snapshot {snapshot} has only {n} rows, which is less than the required {min_rows}.")

def check_nulls(con, snapshot, columns=("store_id", "longitude", "latitude"), max_ratio=0.01):
    """
    Check if any of the specified columns have NULL values for the given snapshot.
    Raises CheckFailed if any NULLs are found.
    """
    for c in columns:
        r = con.execute(f"SELECT AVG(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) FROM stores WHERE snapshot = ?", (snapshot,)).fetchone()[0]
        if r is None:
            raise CheckFailed(f"No rows found for snapshot {snapshot}.")
        if r > max_ratio:
            raise CheckFailed(f"Column {c} has {r:.1%} NULL values, which exceeds the allowed {max_ratio:.1%}.")