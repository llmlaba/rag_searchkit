"""Глобальные настройки проекта (см. docstrings внутри)."""
from dataclasses import dataclass

@dataclass
class Settings:
    """Параметры по умолчанию для CLI и модулей."""
    persist_dir: str = "./chroma_store"
    collection: str = "knb"
    lang: str = "en"
    chunk_size: int = 900
    chunk_overlap: int = 140
    min_section_len: int = 60
    st_model_path: str = "/home/sysadmin/llm/search/st"
    use_half: bool = True
    batch_size_gpu: int = 128
    batch_size_cpu: int = 32
