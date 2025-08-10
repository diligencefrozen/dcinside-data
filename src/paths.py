# src/paths.py
from __future__ import annotations
from pathlib import Path

# ---------- 루트/공용 디렉터리 ----------
def repo_root() -> Path:
    cur = Path.cwd()
    for p in [cur, *cur.parents]:
        if (p / "src").exists():
            return p
    return cur

ROOT = repo_root()
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# 선택: 산출물 하위 폴더(정리용)
STATS = DATA / "stats"
FIGS  = DATA / "figs"
STATS.mkdir(exist_ok=True)
FIGS.mkdir(exist_ok=True)

# ---------- 병합 ----------
ZIP   = DATA / "dcinside-data-main.zip"   # 원본 묶음
MAIN  = DATA / "main.csv"                 # 병합된 원본

# ---------- 정제 ----------
CLEAN = DATA / "main_clean.csv"           # clean_title/clean_body, proxy scores 등

# ---------- 토큰화 ----------
CLEAN_OKT = DATA / "main_clean_okt.parquet"  # OKT 토큰 포함(권장: parquet)

# ---------- 기술통계 ----------
# 표(테이블)
DAILY        = STATS / "daily_posts.csv"
BY_HOUR      = STATS / "posts_by_hour.csv"
BY_WDAY      = STATS / "posts_by_weekday.csv"
BY_AUTHOR    = STATS / "by_author.csv"
TOP_POSTS    = STATS / "top_posts.csv"
TOP_TOKENS   = STATS / "top_tokens.csv"
TOP_BIGRAMS  = STATS / "top_bigrams.csv"
TOP_DOMAINS  = STATS / "top_domains.csv"
ENG_CORR     = STATS / "engagement_corr.csv"

# 그림(옵션)
FIG_HOURLY   = FIGS / "posts_by_hour.png"
FIG_DAILY    = FIGS / "daily_posts.png"
FIG_CORR     = FIGS / "engagement_corr.png"

# ---------- 깃허브 파일들 연동 ----------
# 깃허브 raw 경로에서 data/ 자동 동기화
GITHUB_USER   = "diligencefrozen"   
GITHUB_REPO   = "dcinside-data"     
GITHUB_BRANCH = "main"

REMOTE_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/data"
REMOTE = {
    # 01~03
    "MAIN":       f"{REMOTE_BASE}/main.csv",
    "CLEAN":      f"{REMOTE_BASE}/main_clean.csv",
    "CLEAN_OKT":  f"{REMOTE_BASE}/main_clean_okt.parquet",

    # 04 (stats/)
    "DAILY":       f"{REMOTE_BASE}/stats/daily_posts.csv",
    "BY_HOUR":     f"{REMOTE_BASE}/stats/posts_by_hour.csv",
    "BY_WDAY":     f"{REMOTE_BASE}/stats/posts_by_weekday.csv",
    "BY_AUTHOR":   f"{REMOTE_BASE}/stats/by_author.csv",
    "TOP_POSTS":   f"{REMOTE_BASE}/stats/top_posts.csv",
    "TOP_TOKENS":  f"{REMOTE_BASE}/stats/top_tokens.csv",
    "TOP_BIGRAMS": f"{REMOTE_BASE}/stats/top_bigrams.csv",
    "TOP_DOMAINS": f"{REMOTE_BASE}/stats/top_domains.csv",
    "ENG_CORR":    f"{REMOTE_BASE}/stats/engagement_corr.csv",
}

def ensure_local_from_remote(local_path: Path, remote_url: str, force: bool=False) -> Path:

    if local_path.exists() and not force:
        return local_path
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import requests, shutil
        r = requests.get(remote_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        return local_path
    except Exception:
        # requests가 없거나 실패 시 urllib로 재시도
        from urllib.request import urlopen
        with urlopen(remote_url) as resp, open(local_path, "wb") as f:
            f.write(resp.read())
        return local_path

__all__ = [
    "ROOT","DATA","STATS","FIGS",
    "ZIP","MAIN","CLEAN","CLEAN_OKT",
    "DAILY","BY_HOUR","BY_WDAY","BY_AUTHOR","TOP_POSTS",
    "TOP_TOKENS","TOP_BIGRAMS","TOP_DOMAINS","ENG_CORR",
    "FIG_HOURLY","FIG_DAILY","FIG_CORR",
    "REMOTE","ensure_local_from_remote",
]
