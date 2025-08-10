# src/paths.py
from pathlib import Path

def repo_root() -> Path:
    cur = Path.cwd()
    # 노트북이 어디서 열리든 src가 있는 루트를 찾아감
    for p in [cur, *cur.parents]:
        if (p / "src").exists():
            return p
    return cur

ROOT = repo_root()
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

ZIP = DATA / "dcinside-data-main.zip"
MAIN = DATA / "main.csv"
CLEAN = DATA / "main_clean.csv"
CLEAN_OKT = DATA / "main_clean_okt.parquet"
