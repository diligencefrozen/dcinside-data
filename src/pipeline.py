from __future__ import annotations
from pathlib import Path
import pandas as pd, zipfile, glob

from paths import DATA, ZIP, MAIN, CLEAN, CLEAN_OKT, REMOTE, ensure_local_from_remote
from build_main import build_main
from preprocess import attach_clean_tokens

def ensure_main(force: bool=False) -> Path:
    if MAIN.exists() and not force:
        return MAIN
    # 1) 깃허브 파일 불러오기
    try:
        ensure_local_from_remote(MAIN, REMOTE["MAIN"], force=force)
    except Exception:
        pass
    if MAIN.exists() and not force:
        return MAIN
    # 2) 로컬 data/에서 빌드
    csvs = list(DATA.rglob("*.csv"))
    if not csvs and ZIP.exists():
        with zipfile.ZipFile(ZIP) as z:
            z.extractall(DATA)
    build_main(data_dir=DATA, out_csv=MAIN)
    return MAIN

def ensure_clean(force: bool=False) -> Path:
    if CLEAN.exists() and not force:
        return CLEAN
    try:
        ensure_local_from_remote(CLEAN, REMOTE["CLEAN"], force=force)
    except Exception:
        pass
    if CLEAN.exists() and not force:
        return CLEAN
    ensure_main(False)
    df = pd.read_csv(MAIN)
    df = attach_clean_tokens(df)
    df.to_csv(CLEAN, index=False)
    return CLEAN

def ensure_okt(force: bool=False) -> Path:
    if CLEAN_OKT.exists() and not force:
        return CLEAN_OKT
    import importlib.util
    try:
        from tokenizers import tokenize_okt
    except Exception:
        raise RuntimeError("OKT 토크나이저 모듈(tokenizers.py) 준비가 필요합니다.")
    df = pd.read_csv(CLEAN)
    df["tokens"] = df["clean_body"].fillna("").map(tokenize_okt)
    df.to_parquet(CLEAN_OKT, index=False)
    return CLEAN_OKT

def ensure_all(okt: bool=True, force: bool=False):
    ensure_main(force)
    ensure_clean(force)
    if okt:
        ensure_okt(force)
