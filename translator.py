import json
from urllib import parse, request


class TranslationError(Exception):
    """Raised when a translation request cannot be completed."""


def translate_text(text: str, source_lang: str = "auto", target_lang: str = "tr", timeout: float = 10.0) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""

    params = {
        "client": "gtx",
        "sl": (source_lang or "auto").strip(),
        "tl": (target_lang or "tr").strip(),
        "dt": "t",
        "q": cleaned,
    }
    url = "https://translate.googleapis.com/translate_a/single?" + parse.urlencode(params)

    req = request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
    except Exception as exc:
        raise TranslationError(f"Bağlantı hatası: {exc}") from exc

    try:
        data = json.loads(payload)
        chunks = data[0]
        translated = "".join(part[0] for part in chunks if part and part[0])
    except Exception as exc:
        raise TranslationError("Çeviri yanıtı okunamadı.") from exc

    return translated
