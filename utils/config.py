import os
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_PATH = Path(__file__).parent.parent / ".env"


def load_config() -> dict:
    load_dotenv(ENV_PATH)
    return {
        "NAVER_ID": os.getenv("NAVER_ID", ""),
        "NAVER_PW": os.getenv("NAVER_PW", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    }


def save_config(naver_id: str, naver_pw: str, gemini_key: str):
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(str(ENV_PATH), "NAVER_ID", naver_id)
    set_key(str(ENV_PATH), "NAVER_PW", naver_pw)
    set_key(str(ENV_PATH), "GEMINI_API_KEY", gemini_key)


def get_value(key: str, default: str = "") -> str:
    load_dotenv(ENV_PATH)
    return os.getenv(key, default)
