# src/data_loader.py
from pathlib import Path
import pandas as pd, chardet, io

def smart_read_csv(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    return pd.read_csv(io.BytesIO(raw), encoding=enc, on_bad_lines="skip")

def load_all(csv_dir="post-dataset") -> pd.DataFrame:
    dfs = [smart_read_csv(p) for p in Path(csv_dir).glob("*.csv")]
    return (pd.concat(dfs, ignore_index=True)
              .drop_duplicates("번호")
              .assign(datetime=lambda d: pd.to_datetime(d["상세시간"],
                                                        errors="coerce")))
