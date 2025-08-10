# dcinside-data
디시인사이드 겨울왕국 갤러리 게시글 데이터셋

## 무엇을 담고 있나요?
- 게시물 **병합/정제 → 토큰화(kiwi/okt/regex) → 통계/시각화**까지 재현 가능한 파이프라인
- 커뮤니티 여론 분석 예시(활동량, 시간대, 토큰/바이그램 등)

## 빠른 시작 (Colab/로컬 공통)

~~~bash
git clone https://github.com/diligencefrozen/dcinside-data.git
cd dcinside-data
pip install -r requirements.txt        # (Colab이면 노트북에서 !pip 로 설치)
~~~

> 출력물은 기본적으로 `data/`에 저장됨.  
> - `data/main.csv` (병합 원본)  
> - `data/main_clean.csv` (정제된 데이터)  
> - `data/main_clean_okt.parquet` (예: OKT 토큰화 결과)  
> - `data/top_tokens_*.csv`, `data/top_bigrams_*.csv` 등

## 구조

~~~
dcinside-data/
├─ data/                 # main.csv, 정제본, 토큰 결과 등 산출물
├─ notebooks/
│  ├─ main.ipynb         # 01 병합,정제(메인 드라이버)
│  ├─ 03_tokenize.ipynb  # 03 토큰화(kiwi/okt/regex 선택)
│  └─ 04_analysis.ipynb  # 04 통계,시각화(워드클라우드/시간대/상관분석 등)
├─ src/
│  ├─ build_main.py      # zip/csv 로더 + 병합
│  ├─ preprocess.py      # 정제,정규화 등
│  ├─ tokenizers.py      # tokenize_okt / tokenize_kiwi / tokenize_regex
│  ├─ stats.py           # 토큰/바이그램/도메인,상관 분석
│  ├─ pipeline.py        # ensure_all(okt=True/False)
│  ├─ paths.py           # 공통 경로 상수 (DATA, MAIN, CLEAN, …)
│  └─ korean_setup.py    # 한글 폰트 설정/워드클라우드 폰트 경로
└─ ss/                   # 결과 스샷
~~~

## 결과 맛보기

- **게시물이 가장 많이 업로드된 연도**  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS01.png?raw=true" width="640">

- **이용자들이 자주 활동한 시간대**  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS02.png?raw=true" width="640">

- **엘사 vs 안나**  
  <img src="https://github.com/diligencefrozen/dcinside-data/blob/main/ss/SS03.png?raw=true" width="640">

## 재현 방법 

1) `notebooks/main.ipynb` 실행 → `data/main.csv`, `data/main_clean.csv` 생성  
2) `notebooks/03_tokenize.ipynb` 실행 → `data/main_tokens_*.parquet` 및 토큰/바이그램 랭킹 CSV 생성  
3) `notebooks/04_analysis.ipynb` 실행 → 워드클라우드/시간대/상관분석 등 그림 생성 → `ss/` 저장

## 환경 & 한글 폰트 이슈

한글 깨짐 시:

~~~bash
# Colab/Ubuntu
apt-get -qq update
apt-get -qq install -y fonts-nanum fonts-noto-cjk
~~~

노트북에서:

~~~python
from korean_setup import bootstrap_korean
bootstrap_korean(reset_cache=True)
~~~
