# src/preprocess.py
import re, json
from konlpy.tag import Mecab
MECAB = Mecab()

with open("resources/stopwords_ko.txt") as f:
    STOP = set(f.read().split())

PATTERNS = [r"- dc official App", r"https?://\S+"]

def clean_text(txt: str) -> str:
    if not isinstance(txt, str):
        return ""
    for pat in PATTERNS:
        txt = re.sub(pat, " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def tokenize(txt: str) -> list[str]:
    toks = [t for t, p in MECAB.pos(clean_text(txt))
            if p.startswith(("NN", "VA", "XR")) and t not in STOP]
    return toks
