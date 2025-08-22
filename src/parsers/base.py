"""Интерфейс парсера и преобразование сырья в Chunk'и (to_chunks)."""
from typing import Protocol, List
from dataclasses import dataclass
from src.core.types import Chunk
from src.core.chunking import Chunker, ChunkingParams
from src.core.utils import sha1, detect_section_anchor
import time, os

@dataclass
class RawBlock:
    """Крупный текстовый блок, полученный парсером из источника."""
    source_path: str
    doc_id: str
    order: int
    text: str

class Parser(Protocol):
    """Контракт парсера: parse(path) -> List[RawBlock]."""
    def parse(self, path: str) -> List[RawBlock]: ...

def to_chunks(blocks: List[RawBlock], chunker: Chunker, lang: str = "ru") -> List[Chunk]:
    """RawBlock → Chunk (режем, обогащаем метаданными, выдаём стабильные id)."""
    chunks: List[Chunk] = []
    for b in blocks:
        parts = chunker.split(b.text)
        for i, part in enumerate(parts):
            section, anchor = detect_section_anchor(part)
            content_hash = sha1(part)
            cid = f"{b.doc_id}{anchor}@{content_hash}@{i:04d}"
            meta = {
                "doc_id": b.doc_id,
                "source_path": b.source_path,
                "section": section,
                "anchor": anchor,
                "chunk_index": i,
                "content_hash": content_hash,
                "file_mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.path.getmtime(b.source_path))) if os.path.exists(b.source_path) else "",
                "lang": lang
            }
            chunks.append(Chunk(id=cid, text=part, meta=meta))
    return chunks
