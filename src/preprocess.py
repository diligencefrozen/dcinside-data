# src/preprocess.py
import re, pandas as pd
from collections import Counter

KOREAN = re.compile(r"[가-힣]{2,}")

def clean_text(s: str) -> str:
    if not isinstance(s, str): return ""
    s = re.sub(r"-\s*dc\s+official\s+app", " ", s, flags=re.I)
    s = re.sub(r"From\s+DC\s+Wave", " ", s, flags=re.I)
    s = re.sub(r"이미지\s*순서\s*ON\d*", " ", s, flags=re.I)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"(ㅋ)\1{2,}", r"\1\1", s)
    s = re.sub(r"(ㅎ)\1{2,}", r"\1\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_ko(s: str):
    s = clean_text(s)
    return KOREAN.findall(s)

POS_CUES = ["좋","사랑","감사","행복","기쁘","재밌","귀엽","최고","멋지","축하"]
NEG_CUES = ["싫","짜증","화나","나쁘","불편","최악","혐","빡치","역겹","슬프"]
LAUGHS   = ["ㅋㅋ","ㅎㅎ"]

def sentiment_proxy(s: str):
    if not isinstance(s, str): return 0,0,0
    return (sum(s.count(w) for w in POS_CUES),
            sum(s.count(w) for w in NEG_CUES),
            sum(s.count(w) for w in LAUGHS))

def attach_clean_tokens(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["clean_title"] = df["제목"].map(clean_text)
    df["clean_body"]  = df["내용"].map(clean_text)
    df["tokens"]      = df["clean_body"].map(tokenize_ko)
    df[["pos_hits","neg_hits","laugh_hits"]] = df["clean_body"].apply(
        lambda t: pd.Series(sentiment_proxy(t))
    )
    return df
