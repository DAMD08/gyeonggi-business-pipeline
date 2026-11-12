import re, shutil, sys
from pathlib import Path
RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

def ingest(src, raw=RAW):
    """
    Ingests data from the source directory to the raw directory.

    Args:
        src (str): The source directory containing the data to be ingested.
        raw (Path): The destination directory for raw data.
    """
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    m = re.search(r"_(\d{6})\.csv$", src.name)
    if not m:
        raise ValueError(f"Source file name must end with '_YYYYMM.csv', got: {src.name}")
    dst = raw / f"gyeonggi_{m[1]}.csv"
    if dst.exists():
        raise FileExistsError(f"Destination file already exists: {dst}")
    raw.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    shutil.copy2(src, tmp)
    if tmp.stat().st_size != src.stat().st_size:
        raise OSError(f"incomplete copy: {tmp}")
    tmp.replace(dst)
    return dst

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python src/ingest.py <source_file>")
    try:
        print(ingest(sys.argv[1]))
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        sys.exit(f"Error: {e}")