from __future__ import annotations
import os, glob, shutil, subprocess
from typing import Optional, Dict

import matplotlib as mpl
from matplotlib import font_manager as fm

__all__ = [
    "bootstrap_korean",
    "setup_korean",
    "wordcloud_font_path",
    "test_plot",
]

# 대표 후보 경로/이름 (Colab/우분투 기준)
_CAND_PATHS = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/**/NanumGothic*.ttf",
    "/usr/share/fonts/**/NotoSansCJK*.*",
]
_CAND_NAMES = ("NanumGothic", "Noto Sans CJK KR", "Noto Sans KR", "Noto Sans CJK")


def _rebuild_cache() -> None:

    try:
        shutil.rmtree(mpl.get_cachedir(), ignore_errors=True)
    except Exception:
        pass
    try:
        fm._load_fontmanager(try_read_cache=False)  # pylint: disable=protected-access
    except Exception:
        pass


def _find_font_path() -> Optional[str]:

    # 1) 경로 패턴으로 탐색
    for pattern in _CAND_PATHS:
        for p in glob.glob(pattern, recursive=True):
            if os.path.exists(p):
                return p
    # 2) 폰트명으로 탐색
    for name in _CAND_NAMES:
        try:
            path = fm.findfont(name, fallback_to_default=False)
            if path and os.path.exists(path):
                return path
        except Exception:
            pass
    return None


def setup_korean(reset_cache: bool = False) -> Dict[str, Optional[str]]:
    """
    Matplotlib 전역 한글 폰트 설정.
    반환값: {"font_path": str|None, "family": str|None, "ok": bool}
    """
    if reset_cache:
        _rebuild_cache()
    else:
        try:
            fm._load_fontmanager(try_read_cache=False)  # pylint: disable=protected-access
        except Exception:
            pass

    path = _find_font_path()
    family = None

    if path:
        try:
            fm.fontManager.addfont(path)  # 직접 등록
        except Exception:
            pass
        prop = fm.FontProperties(fname=path)
        family = prop.get_name()

        # 전역 적용 + 폴백 후보 추가
        mpl.rcParams["font.family"] = family
        mpl.rcParams["font.sans-serif"] = [family, *_CAND_NAMES, *mpl.rcParams.get("font.sans-serif", [])]
    else:
        # 폰트를 못 찾았을 때도 최대한 폴백
        mpl.rcParams["font.family"] = "sans-serif"
        mpl.rcParams["font.sans-serif"] = [*_CAND_NAMES, *mpl.rcParams.get("font.sans-serif", [])]

    mpl.rcParams["axes.unicode_minus"] = False  # 마이너스 깨짐 방지
    return {"font_path": path, "family": family, "ok": bool(path)}


def bootstrap_korean(auto_install: bool = True) -> Dict[str, Optional[str]]:

    info = setup_korean(reset_cache=False)
    if info["ok"] or not auto_install:
        return info

    # apt-get이 있으면 Colab/리눅스 환경으로 가정하고 설치 시도
    if shutil.which("apt-get"):
        try:
            subprocess.run(["apt-get", "-qq", "update"], check=False, capture_output=True)
            subprocess.run(
                ["apt-get", "-qq", "install", "-y", "fonts-nanum", "fonts-noto-cjk"],
                check=False, capture_output=True
            )
        except Exception:
            # 설치 실패해도 계속 진행하며 다시 세팅 시도
            pass
        info = setup_korean(reset_cache=True)

    return info


def wordcloud_font_path() -> Optional[str]:

    return setup_korean(reset_cache=False).get("font_path")


def test_plot() -> None:

    import matplotlib.pyplot as plt
    info = setup_korean(reset_cache=False)
    prop = fm.FontProperties(fname=info["font_path"]) if info["font_path"] else None

    plt.figure()
    plt.plot([1, 2, 3])
    plt.title("테스트= 겨울왕국", fontproperties=prop)
    plt.xlabel("가로축 라벨", fontproperties=prop)
    plt.ylabel("세로축 라벨", fontproperties=prop)
    plt.tight_layout()
    plt.show()
