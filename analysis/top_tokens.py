# analysis/top_tokens.py
from collections import Counter
def top_k(df, k=50):
    counter = Counter()
    for toks in df["본문_tokens"]:
        counter.update(toks)
    return counter.most_common(k)
