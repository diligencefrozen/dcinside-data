# dcinside-data
DCInside Frozen Gallery Posts Dataset

## What’s inside?
- A **reproducible pipeline** from **merge/clean → tokenization (kiwi/okt/regex) → stats/visualization**
- Community analysis examples (activity volume, active hours, token/bigram rankings, etc.)

## Quick start (Colab or local)

~~~bash
git clone https://github.com/diligencefrozen/dcinside-data.git
cd dcinside-data
pip install -r requirements.txt        # On Colab, use !pip inside the notebook
~~~

> Outputs are written to `data/` by default.  
> - `data/main.csv` (merged raw posts)  
> - `data/main_clean.csv` (cleaned dataset)  
> - `data/main_clean_okt.parquet` (e.g., OKT tokenization result)  
> - `data/top_tokens_*.csv`, `data/top_bigrams_*.csv`, etc.

## Preview

- **Year with the most posts**  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS01.png?raw=true" width="640">

- **Hours with the most activity**  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS02.png?raw=true" width="640">

- **Elsa vs Anna **  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS03.png?raw=true" width="640">
  <br>Elsa(Orange), Anna(Blue), (Frozen = Green)

## How to reproduce

1) Run `notebooks/main.ipynb` → creates `data/main.csv` and `data/main_clean.csv`  
2) Run `notebooks/03_tokenize.ipynb` → creates `data/main_tokens_*.parquet` and token/bigram ranking CSVs  
3) Run `notebooks/04_analysis.ipynb` → generates wordcloud/hourly/correlation figures → save to `ss/`

## Environment & Korean font issues

If Korean text is garbled:

~~~bash
# Colab/Ubuntu
apt-get -qq update
apt-get -qq install -y fonts-nanum fonts-noto-cjk
~~~

In notebooks:

~~~python
from korean_setup import bootstrap_korean
bootstrap_korean(reset_cache=True)
~~~
