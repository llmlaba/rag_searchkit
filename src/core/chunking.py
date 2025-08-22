"""Интерфейсы и реализации для разбиения текста на чанки."""
from typing import List, Protocol
from dataclasses import dataclass
import re

@dataclass
class ChunkingParams:
    """Параметры чанкера."""
    chunk_size: int = 900
    overlap: int = 140
    min_len: int = 60

class Chunker(Protocol):
    """Контракт на стратегию разбиения: split(text) -> List[str]."""
    def split(self, text: str) -> List[str]: ...

class HeaderAwareChunker:
    """Чанкёр: по заголовкам → затем скользящим окном с overlap."""
    def __init__(self, params: ChunkingParams):
        self.p = params
    def split(self, text: str) -> List[str]:
        """Вернуть список «пассажей» для индексации."""
        blocks = re.split(r"\n(?=(?:#{1,6}\s))", text)
        chunks: List[str] = []
        step = max(1, self.p.chunk_size - self.p.overlap)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            i = 0; n = len(block)
            while i < n:
                piece = block[i:i+self.p.chunk_size].strip()
                if len(piece) >= self.p.min_len:
                    chunks.append(piece)
                i += step
        return chunks
