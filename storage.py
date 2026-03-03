import json
import os
from typing import Dict, Any

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(APP_DIR, "progress.json")

DEFAULT_PROGRESS: Dict[str, Any] = {
    "xp": 0,
    "completed_lessons": [],
    "completed_units": [],
    "badges": [],
    "quiz_completed": [],
    "quiz_streak": 0,
    "auto_next": True,
    "last_lesson_id": "",
    "avatar_id": "default",
    "coins": 0,
}

def load_progress() -> Dict[str, Any]:
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return dict(DEFAULT_PROGRESS)
        merged = dict(DEFAULT_PROGRESS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_PROGRESS)

def save_progress(progress: Dict[str, Any]) -> None:
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def reset_progress() -> None:
    try:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
    except Exception:
        pass
