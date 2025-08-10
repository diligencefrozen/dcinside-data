# -*- coding: utf-8 -*-
# Pipeline: load fragmented CSVs -> merge to main.csv -> clean -> tokenization -> stats
# Works directly on the uploaded /mnt/data/dcinside-data-main.zip

import zipfile, io, re, os, math, json, pandas as pd, numpy as np
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from caas_jupyter_tools import display_dataframe_to_user

ZIP_PATH = "/mnt/data/dcinside-data-main.zip"
OUT_MAIN = "/mnt/data/main.csv"
OUT_CLEAN = "/mnt/data/main_clean.csv"
OUT_TOKEN = "/mnt/data/top_tokens.csv"
OUT_BIGRAM = "/mnt/data/top_bigrams.csv"
OUT_DOMAINS = "/mnt/data/top_domains.csv"

# ---------- Helpers ----------
ENCODINGS = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

def try_read_csv_from_bytes(b):
    last_err = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(io.BytesIO(b), encoding=enc, on_bad_lines="skip")
        except Exception as e:
            last_err = e
            continue
    raise last_err

def clean_text(s: str) -> str:
    """Lightweight cleaner focused on DCInside artifacts"""
    if not isinstance(s, str):
        return ""
    # Remove DC app signature & common boilerplate
    s = re.sub(r"-\s*dc\s+official\s+app", " ", s, flags=re.I)
    s = re.sub(r"From\s+DC\s+Wave", " ", s, flags=re.I)
    # Remove image ordering artifacts like "이미지 순서 ON2" or "이미지 순서 ON 3"
    s = re.sub(r"이미지\s*순서\s*ON\d*", " ", s, flags=re.I)
    # Strip URLs
    s = re.sub(r"https?://\S+", " ", s)
    # Strip HTML-ish leftovers
    s = re.sub(r"<[^>]+>", " ", s)
    # Normalize laughter spam like ㅋㅋㅋㅋ -> ㅋㅋ
    s = re.sub(r"(ㅋ)\1{2,}", r"\1\1", s)
    s = re.sub(r"(ㅎ)\1{2,}", r"\1\1", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Korean-only tokenization (no external libs): sequences of Korean chars length >=2
KOREAN_RE = re.compile(r"[가-힣]{2,}")

def tokenize_ko(s: str):
    if not isinstance(s, str):
        return []
    s = clean_text(s)
    return KOREAN_RE.findall(s)

# Basic (very rough) sentiment/subjectivity proxy using tiny lexicons
POS_CUES = ["좋", "사랑", "감사", "행복", "기쁘", "재밌", "귀엽", "최고", "멋지", "축하"]
NEG_CUES = ["싫", "짜증", "화나", "나쁘", "불편", "최악", "혐", "빡치", "역겹", "슬프"]
LAUGHTER = ["ㅋㅋ", "ㅎㅎ"]

def sentiment_proxy(text: str):
    """Return tiny heuristic scores (pos, neg, laugh)."""
    if not isinstance(text, str): 
        return 0, 0, 0
    t = text
    p = sum(t.count(w) for w in POS_CUES)
    n = sum(t.count(w) for w in NEG_CUES)
    l = sum(t.count(w) for w in LAUGHTER)
    return p, n, l

# ---------- Load & merge ----------
if not os.path.exists(ZIP_PATH):
    raise FileNotFoundError("Uploaded zip not found at /mnt/data/dcinside-data-main.zip")

with zipfile.ZipFile(ZIP_PATH) as z:
    csv_members = [name for name in z.namelist() 
                   if name.lower().endswith(".csv") and "post-dataset" in name.lower()]
    if not csv_members:
        # Fallback: any csv in zip
        csv_members = [name for name in z.namelist() if name.lower().endswith(".csv")]

    frames = []
    loaded = 0
    for name in sorted(csv_members):
        try:
            b = z.read(name)
            df = try_read_csv_from_bytes(b)
            df["__source"] = name
            frames.append(df)
            loaded += 1
        except Exception as e:
            print("Failed to read:", name, "->", e)

if not frames:
    raise RuntimeError("No CSVs could be read from the zip.")

df = pd.concat(frames, ignore_index=True)

# Ensure expected columns exist even if missing in some shards
for col in ["번호","제목","제목url","댓글","글쓴이","글쓴이ip","조회","추천","상세시간","내용","첨부이미지"]:
    if col not in df.columns:
        df[col] = np.nan

# Deduplicate by 게시물 번호 if present
if "번호" in df.columns:
    df = df.drop_duplicates(subset=["번호"])

# Parse datetime
if "상세시간" in df.columns:
    # Try a few formats
    def parse_dt(x):
        if pd.isna(x): 
            return pd.NaT
        for fmt in ["%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
            try:
                return datetime.strptime(str(x), fmt)
            except Exception:
                continue
        try:
            return pd.to_datetime(x, errors="coerce")
        except Exception:
            return pd.NaT
    df["datetime"] = df["상세시간"].apply(parse_dt)
else:
    df["datetime"] = pd.NaT

# Save merged main.csv
df.to_csv(OUT_MAIN, index=False)

# ---------- Cleaning & tokenization ----------
df["clean_title"] = df["제목"].apply(clean_text)
df["clean_body"] = df["내용"].apply(clean_text)

# Sentiment proxy counts on cleaned body
sents = df["clean_body"].apply(sentiment_proxy)
df["pos_hits"] = sents.apply(lambda x: x[0])
df["neg_hits"] = sents.apply(lambda x: x[1])
df["laugh_hits"] = sents.apply(lambda x: x[2])

# Tokenize
df["tokens"] = df["clean_body"].apply(tokenize_ko)

# Save cleaned
df.to_csv(OUT_CLEAN, index=False)

# ---------- Stats ----------
# Activity over time
ts_daily = (df.dropna(subset=["datetime"])
              .assign(date=lambda d: d["datetime"].dt.date)
              .groupby("date").size().reset_index(name="posts"))

# Hourly/weekday patterns
time_df = df.dropna(subset=["datetime"]).copy()
time_df["hour"] = time_df["datetime"].dt.hour
time_df["weekday"] = time_df["datetime"].dt.weekday  # 0=Mon

by_hour = time_df.groupby("hour").size().reset_index(name="posts")
by_wday = time_df.groupby("weekday").size().reset_index(name="posts")

# Authors (top posters, top by avg 추천)
by_author = (df.groupby("글쓴이")
               .agg(posts=("번호","count"),
                    avg_rec=("추천", "mean"),
                    avg_view=("조회", "mean"))
               .sort_values("posts", ascending=False)
               .reset_index())

# Top posts by 추천
top_posts = df.sort_values(["추천","조회"], ascending=False).head(50)

# Token frequency
token_counter = Counter()
for row in df["tokens"]:
    token_counter.update(row)

top_tokens = pd.DataFrame(token_counter.most_common(200), columns=["token","count"])

# Bigrams (within post body level)
bigram_counter = Counter()
for toks in df["tokens"]:
    for a, b in zip(toks, toks[1:]):
        bigram_counter[(a,b)] += 1
top_bigrams = pd.DataFrame([(f"{a} {b}", c) for (a,b), c in bigram_counter.most_common(200)],
                           columns=["bigram","count"])

# Domain extraction from body URLs
def extract_urls(text):
    if not isinstance(text, str): 
        return []
    return re.findall(r"https?://[^\s)\"']+", text)

domains = Counter()
for text in df["내용"].fillna("").astype(str):
    for u in extract_urls(text):
        try:
            d = urlparse(u).netloc.lower()
            if d:
                domains[d] += 1
        except Exception:
            pass
top_domains = pd.DataFrame(domains.most_common(100), columns=["domain","count"])

# Engagement correlations
eng_cols = ["조회","추천","댓글","pos_hits","neg_hits","laugh_hits"]
corr_df = df[eng_cols].apply(pd.to_numeric, errors="coerce").corr()

# Save stat CSVs
top_tokens.to_csv(OUT_TOKEN, index=False)
top_bigrams.to_csv(OUT_BIGRAM, index=False)
top_domains.to_csv(OUT_DOMAINS, index=False)

# ---------- Present to user ----------
# 1) Show merged sample
display_dataframe_to_user("Merged posts sample (first 30)", df.head(30))

# 2) Show summary tables
display_dataframe_to_user("Daily post volume", ts_daily.tail(30))
display_dataframe_to_user("Top authors by posts", by_author.head(30))
display_dataframe_to_user("Top tokens (Korean only)", top_tokens.head(50))
display_dataframe_to_user("Top bigrams", top_bigrams.head(50))
display_dataframe_to_user("Top external domains in body", top_domains.head(50))
display_dataframe_to_user("Top posts by 추천", top_posts[["번호","제목","추천","조회","댓글","datetime"]].head(30))

# 3) Simple charts (matplotlib; no specific colors)
# Posts by hour
plt.figure(figsize=(8,4))
plt.plot(by_hour["hour"], by_hour["posts"], marker="o")
plt.title("Posts by Hour")
plt.xlabel("Hour of day (0-23)")
plt.ylabel("Posts")
plt.tight_layout()
plt.show()

# Daily time series (if not too long, plot last 90 days)
if len(ts_daily) > 0:
    tail = ts_daily.tail(min(90, len(ts_daily)))
    plt.figure(figsize=(10,4))
    plt.plot(pd.to_datetime(tail["date"]), tail["posts"], marker="o")
    plt.title("Daily Posts (last window)")
    plt.xlabel("Date")
    plt.ylabel("Posts")
    plt.tight_layout()
    plt.show()

# 4) Correlation heatmap via Matplotlib (no seaborn). Keep it simple.
# We'll render as imshow with numeric ticks to avoid Korean font issues.
fig = plt.figure(figsize=(5,4))
ax = plt.gca()
im = ax.imshow(corr_df.values, aspect="auto")
ax.set_xticks(range(len(corr_df.columns)))
ax.set_yticks(range(len(corr_df.columns)))
ax.set_xticklabels(corr_df.columns, rotation=45, ha="right")
ax.set_yticklabels(corr_df.columns)
plt.title("Engagement correlations")
plt.tight_layout()
plt.show()

# Prepare result file paths for the chat message
result_paths = {
    "main.csv": OUT_MAIN,
    "main_clean.csv": OUT_CLEAN,
    "top_tokens.csv": OUT_TOKEN,
    "top_bigrams.csv": OUT_BIGRAM,
    "top_domains.csv": OUT_DOMAINS
}
print(result_paths)
