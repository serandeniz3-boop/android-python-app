from typing import Optional

def safe_toast(text: str) -> None:
    try:
        from kivymd.uix.snackbar import Snackbar as _SB
        try:
            _SB(text=text).open()
        except Exception:
            _SB(text).open()
    except Exception:
        print(text)

def get_progressbar_class():
    try:
        from kivymd.uix.progressbar import MDProgressBar
        return MDProgressBar
    except Exception:
        try:
            from kivy.uix.progressbar import ProgressBar
            return ProgressBar
        except Exception:
            return None
