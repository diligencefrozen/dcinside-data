# src/stats.py
import re, pandas as pd
from collections import Counter
from urllib.parse import urlparse

def activity(df: pd.DataFrame):
    t = df.dropna(subset=["datetime"]).copy()
    t["date"] = t["datetime"].dt.date
    daily   = t.groupby("date").size().reset_index(name="posts")
    hourly  = t.groupby(t["datetime"].dt.hour).size().reset_index(name="posts").rename(columns={"datetime":"hour"})
    wday    = t.groupby(t["datetime"].dt.weekday).size().reset_index(name="posts").rename(columns={"datetime":"weekday"})
    return daily, hourly, wday

def authors(df: pd.DataFrame):
    g = (df.groupby("글쓴이")
           .agg(posts=("번호","count"),
                avg_rec=("추천","mean"),
                avg_view=("조회","mean"))
           .sort_values("posts", ascending=False)
           .reset_index())
    return g

def tokens_bigrams(df: pd.DataFrame, topn=200):
    tok = Counter()
    bi  = Counter()
    for toks in df["tokens"]:
        tok.update(toks)
        for a,b in zip(toks, toks[1:]):
            bi[(a,b)] += 1
    top_tokens  = pd.DataFrame(tok.most_common(topn), columns=["token","count"])
    top_bigrams = pd.DataFrame([(f"{a} {b}", c) for (a,b),c in bi.most_common(topn)], columns=["bigram","count"])
    return top_tokens, top_bigrams

def body_domains(df: pd.DataFrame, topn=100):
    pat = re.compile(r"https?://[^\s)\"']+")
    domains = Counter()
    for text in df["내용"].fillna("").astype(str):
        for u in pat.findall(text):
            try:
                d = urlparse(u).netloc.lower()
                if d: domains[d] += 1
            except: pass
    return pd.DataFrame(domains.most_common(topn), columns=["domain","count"])

def correlations(df: pd.DataFrame):
    cols = ["조회","추천","댓글","pos_hits","neg_hits","laugh_hits"]
    return df[cols].apply(pd.to_numeric, errors="coerce").corr()
