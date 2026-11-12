import re, shutil, sys
from pathlib import Path

def ingest(src, raw=Path("data/raw"), processed=Path("data/processed")):
    """
    Ingests data from the source directory to the raw and processed directories.

    Args:
        src (str): The source directory containing the data to be ingested.
        raw (Path): The destination directory for raw data.
        processed (Path): The destination directory for processed data.
    """
    src_path = Path(src)
    m = re.search(r"_(\d{6})\.csv$", src_path.name)
    if not m:
        raise ValueError(f"Source file name must end with '_YYYYMM.csv', got: {src_path.name}")
    dst = raw / f"gyeonggi_{m[1]}.csv"
    if dst.exists():
        raise FileExistsError(f"Destination file already exists: {dst}")
    raw.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_path, dst)
    return dst

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python src/ingest.py <source_file>")
    try:
        print(ingest(sys.argv[1]))
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        sys.exit(f"Error: {e}")