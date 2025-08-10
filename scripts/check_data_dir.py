# scripts/check_data_dir.py
import os, glob, json

def main():
    base = "/mnt/data"  # 바꾸려면 여기 수정
    candidates = {
        "zips": glob.glob(os.path.join(base, "*.zip")),
        "csvs": glob.glob(os.path.join(base, "*.csv")),
        "dirs": [p for p in glob.glob(os.path.join(base, "*")) if os.path.isdir(p)],
    }
    print(json.dumps(candidates, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
