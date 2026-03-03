import contextlib
import io
import traceback
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RunResult:
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    env: Dict[str, Any] = None

def run_user_code(code: str, input_text: str = "", timeout_s: float = 2.5) -> RunResult:
    import threading
    import builtins

    res = RunResult(stdout="", stderr="", error="", env={})
    input_lines = (input_text or "").splitlines()
    it = iter(input_lines)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            return ""

    def _run():
        local_env = {}
        g = {"__name__": "__main__"}
        old_input = builtins.input
        builtins.input = fake_input
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                exec(code, g, local_env)
            res.stdout = out_buf.getvalue()
            res.stderr = err_buf.getvalue()
            res.env = local_env
        except Exception:
            res.error = traceback.format_exc()
            res.stdout = out_buf.getvalue()
            res.stderr = err_buf.getvalue()
            res.env = local_env
        finally:
            builtins.input = old_input

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    th.join(timeout=timeout_s)
    if th.is_alive():
        res.error = f"TimeoutError: Kod {timeout_s} saniyede bitmedi."
    return res
