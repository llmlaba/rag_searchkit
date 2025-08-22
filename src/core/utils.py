\
"""Утилиты: хеширование, slug, извлечение заголовка/якоря."""
import re, hashlib, unicodedata
from typing import Tuple

def sha1(s: str) -> str:
    """Короткий SHA1-хеш (8 символов) для стабильных id по содержимому."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]

def slug(s: str) -> str:
    """Сделать slug: нижний регистр, символы/цифры/дефисы/подчёркивания."""
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^\w\- ]+", "", s, flags=re.UNICODE).strip().lower().replace(" ", "-")
    return s

def detect_section_anchor(text: str) -> Tuple[str, str]:
    """Найти первый заголовок и сгенерировать якорь (#anchor)."""
    m = re.search(r"^(#{1,6})\s+(.+)$", text, flags=re.MULTILINE)
    if not m:
        return "", ""
    title = m.group(2).strip()
    anchor = "#" + re.sub(r"[^\w\- ]", "", title).strip().lower().replace(" ", "-")
    return title, anchor
