"""Базовые типы данных для пайплайна семантического поиска."""
from dataclasses import dataclass
from typing import Dict, Any

Metadata = Dict[str, Any]

@dataclass
class Chunk:
    """Единица индексации: небольшой кусок текста с метаданными."""
    id: str           # стабильный уникальный идентификатор
    text: str         # очищенный текст чанка
    meta: Metadata    # словарь метаданных (источник, якорь, индекс, язык и т.д.)

@dataclass
class QueryHit:
    """Результат поиска (top-K соседей по эмбеддингу)."""
    text: str
    meta: Metadata
    distance: float   # чем меньше, тем ближе
