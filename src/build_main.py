# src/build_main.py
from pathlib import Path
import zipfile, io, pandas as pd

ENCODINGS = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

def _read_bytes_csv(b: bytes) -> pd.DataFrame:
    last = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(io.BytesIO(b), encoding=enc, on_bad_lines="skip")
        except Exception as e:
            last = e
    raise last

def _read_csv_file(p: Path) -> pd.DataFrame:
    last = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(p, encoding=enc, on_bad_lines="skip")
        except Exception as e:
            last = e
    raise last

def build_main(data_dir="data", out_csv="data/main.csv") -> pd.DataFrame:
    data_dir = Path(data_dir)
    zip_paths = list(data_dir.glob("*.zip"))
    csv_paths = list(data_dir.glob("*.csv"))

    frames = []
    if zip_paths:
        # zip 안에서 post-dataset/*.csv 전부 읽기
        with zipfile.ZipFile(zip_paths[0]) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            # post-dataset 우선
            names = sorted(names, key=lambda x: (0 if "post-dataset" in x.lower() else 1, x))
            for n in names:
                try:
                    df = _read_bytes_csv(z.read(n))
                    frames.append(df)
                except Exception:
                    pass
    elif csv_paths:
        for p in sorted(csv_paths):
            try:
                frames.append(_read_csv_file(p))
            except Exception:
                pass
    else:
        raise FileNotFoundError("data/에 zip 또는 csv가 없습니다.")

    if not frames:
        raise RuntimeError("CSV를 읽지 못했습니다. 인코딩/파일 확인 요망.")

    df = pd.concat(frames, ignore_index=True)

    # 컬럼 가드
    for c in ["번호","제목","제목url","댓글","글쓴이","글쓴이ip","조회","추천","상세시간","내용","첨부이미지"]:
        if c not in df.columns:
            df[c] = pd.NA

    # 중복 제거 + 날짜 파싱
    df = df.drop_duplicates(subset=["번호"], ignore_index=True)
    def _parse(x):
        for fmt in ("%Y.%m.%d %H:%M:%S","%Y-%m-%d %H:%M:%S","%Y/%m/%d %H:%M:%S"):
            try: return pd.to_datetime(x, format=fmt)
            except Exception: pass
        return pd.to_datetime(x, errors="coerce")
    df["datetime"] = df["상세시간"].apply(_parse)

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df
