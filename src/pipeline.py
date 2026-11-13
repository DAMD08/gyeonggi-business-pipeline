import argparse, sqlite3, sys
from datetime import date
from pathlib import Path
from src import checks
from src.ingest import ingest, RAW
from src.stage import stage, DB

SCHEMA = Path(__file__).parent.parent / "schema" / "expected_header.csv"

def run(source, allow_stale=False):
    source = Path(source)
    if not source.exists():
        print(f"Source file {source} does not exist.", file=sys.stderr)
        sys.exit(1)
    snapshot = source.stem[-6:]
    try:
        raw = ingest(source)
    except FileExistsError:
        raw = RAW / f"gyeonggi_{snapshot}.csv"
        print(f"File {raw} already exists. Using existing file.")
    checks.check_duplicates(raw)
    checks.check_schema(raw, SCHEMA)
    print(f"staged {stage(raw)} rows to {DB}")
    with sqlite3.connect(DB) as con:
        checks.check_volume(con, snapshot, 500_000)
        checks.check_nulls(con, snapshot)
        try:
            checks.check_freshness(con, date.today())
        except checks.CheckFailed as e:
            if not allow_stale:
                raise
            print(f"Warning: {e}. Continuing because --allow-stale is set.")
    print(f"Pipeline ok for snapshot {snapshot}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run data pipeline checks.")
    parser.add_argument("source", help="Path to the source CSV file.")
    parser.add_argument("--allow-stale", action="store_true", help="Allow stale data without failing.")
    args = parser.parse_args()
    try:
        run(args.source, allow_stale=args.allow_stale)
    except (checks.CheckFailed, ValueError, FileNotFoundError) as e:
        print(f"Pipeline stopped: {e}", file=sys.stderr)
        sys.exit(1)