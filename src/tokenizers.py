# src/tokenizers.py
from konlpy.tag import Okt
from preprocess import clean_text

_okt = None
def get_okt():
    global _okt
    if _okt is None:
        _okt = Okt()
    return _okt

def tokenize_okt(text: str):
    t = clean_text(text) if isinstance(text, str) else ""
    okt = get_okt()
    toks = []
    for w, pos in okt.pos(t, norm=True, stem=True):
        if pos in {"Noun","Verb","Adjective"} and len(w) >= 2:
            toks.append(w)
    return toks
