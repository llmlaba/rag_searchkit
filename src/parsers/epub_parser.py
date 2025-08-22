"""Парсер EPUB: HTML→plain-текст с лёгкой нормализацией."""
from typing import List
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import re, html
from .base import RawBlock, Parser
from ..core.utils import slug

def _norm_ws(s: str) -> str:
    """Нормализовать пробелы/переносы для читаемости и стабильности чанков."""
    s = re.sub(r"\s+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()

def _html_to_text(html_bytes: bytes) -> str:
    """HTML→текст (только для EPUB-парсера, чтобы core не зависел от BeautifulSoup)."""
    soup = BeautifulSoup(html_bytes, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for pre in soup.find_all("pre"):
        txt = pre.get_text("\n", strip=False)
        pre.replace_with("\n```\n" + txt + "\n```\n")
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td","th"])]
            if cells:
                rows.append(" | ".join(cells))
        table.replace_with("\n".join(rows) + "\n")
    for li in soup.find_all("li"):
        li.insert_before("\n- ")
    text = soup.get_text("\n", strip=False)
    text = re.sub(r"\n{0,2}(?P<h>(Chapter|Глава)\s+\d+[:.]?.*)\n", r"\n# \g<h>\n", text, flags=re.IGNORECASE)
    text = html.unescape(text)
    return _norm_ws(text)

class EpubParser:
    """Простой парсер ePub, возвращает список RawBlock (по одному на HTML-страницу)."""
    def parse(self, path: str) -> List[RawBlock]:
        book = epub.read_epub(path)
        title = (book.get_metadata('DC', 'title') or [["untitled"]])[0][0]
        book_id = slug(title)
        items = [i for i in book.get_items() if i.get_type() == ITEM_DOCUMENT]
        blocks: List[RawBlock] = []
        for order, item in enumerate(items):
            href = item.get_name() or item.file_name or f"item_{order}.xhtml"
            text = _html_to_text(item.get_content())
            if not text:
                continue
            blocks.append(RawBlock(
                source_path=href,
                doc_id=f"{book_id}/{href}",
                order=order,
                text=text
            ))
        return blocks
