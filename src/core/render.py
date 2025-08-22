\
"""Форматирование и вывод результатов поиска (pretty/jsonl/tsv)."""
from typing import List
from src.core.types import QueryHit
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
import re, json

def _highlight(text: str, query: str, max_len: int = 900) -> str:
    """Подсветить ключевые слова запроса и обрезать сниппет до max_len."""
    snippet = text[:max_len]
    words = [w for w in re.split(r"[^\w\-]+", query.lower()) if len(w) >= 3]
    for w in set(words):
        snippet = re.sub(rf"(?i)\b({re.escape(w)})\b", r"[bold]\1[/bold]", snippet)
    return snippet

def pretty(query: str, hits: List[QueryHit]) -> None:
    """Вывод в терминал: таблица + панели со сниппетами и метаданными."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=3)
    table.add_column("Источник", overflow="fold")
    table.add_column("Секция", overflow="fold")
    table.add_column("Chunk ID/Index", overflow="fold")
    table.add_column("Distance", justify="right", width=10)
    for i, h in enumerate(hits, 1):
        src = f"{h.meta.get('source_path','')}{h.meta.get('anchor','')}"
        sec = h.meta.get("section","")
        chid = f"{h.meta.get('chunk_index','?')} | {h.meta.get('content_hash','')}"
        table.add_row(str(i), src, sec, chid, f"{h.distance:.4f}")
    rprint(table)
    for i, h in enumerate(hits, 1):
        header = f"[{i}] {h.meta.get('source_path','')} {h.meta.get('anchor','')} (chunk {h.meta.get('chunk_index','?')})"
        rprint(Panel.fit(Markdown(_highlight(h.text, query)), title=header, border_style="cyan"))

def jsonl(hits: List[QueryHit]) -> str:
    """Сериализовать результаты как JSON Lines — удобно для LLM или пайплайнов."""
    lines = []
    for i, h in enumerate(hits, 1):
        obj = {"rank": i, "distance": h.distance, "text": h.text, "meta": h.meta}
        lines.append(json.dumps(obj, ensure_ascii=False))
    return "\n".join(lines)

def tsv(hits: List[QueryHit]) -> str:
    """Сериализовать результаты как TSV (табличный текст)."""
    out = ["rank\tdistance\tsource\tsection\tchunk_index\tanchor\ttext"]
    for i, h in enumerate(hits, 1):
        out.append("\t".join([
            str(i),
            f"{h.distance:.4f}",
            str(h.meta.get("source_path","")),
            str(h.meta.get("section","")),
            str(h.meta.get("chunk_index","")),
            str(h.meta.get("anchor","")),
            h.text.replace("\n"," \\n ")
        ]))
    return "\n".join(out)
