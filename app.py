#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI: индексация EPUB и поиск по индексу (без LLM)."""
import argparse, time
from typing import List
from config import Settings

from src import logger
from src.core.chunking import HeaderAwareChunker, ChunkingParams
from src.core.embeddings import STEmbedder, STConfig
from src.core.vectordb import ChromaStore, ChromaConfig
from src.core.render import pretty, jsonl, tsv
from src.core.types import Chunk, QueryHit
from src.parsers.base import Parser, to_chunks
from src.parsers.epub_parser import EpubParser

def get_embedder(cfg: Settings) -> STEmbedder:
    """Инициализация SentenceTransformers-энкодера (CPU/GPU)."""
    return STEmbedder(STConfig(model_name=cfg.st_model_path, use_half=cfg.use_half))

def build_epub(epub_path: str, cfg: Settings) -> None:
    """Индексировать EPUB: parse → chunk → embed → store."""
    parser: Parser = EpubParser()
    blocks = parser.parse(epub_path)

    chunker = HeaderAwareChunker(ChunkingParams(cfg.chunk_size, cfg.chunk_overlap, cfg.min_section_len))
    chunks: List[Chunk] = to_chunks(blocks, chunker, lang=cfg.lang)
    logger.info(f"[build] сырьевых блоков: {len(blocks)} | чанков: {len(chunks)}")

    emb = get_embedder(cfg)
    t0 = time.time()
    batch = cfg.batch_size_gpu if getattr(emb, "device", "cpu").startswith("cuda") else cfg.batch_size_cpu
    vecs = emb.encode([c.text for c in chunks], batch_size=batch)
    logger.info(f"[build] эмбеддинги: {len(vecs)} | время: {time.time()-t0:.1f}s | embedder={emb.name}")

    store = ChromaStore(ChromaConfig(persist_dir=cfg.persist_dir, collection=cfg.collection))
    store.reset()
    store.add(chunks, vecs)
    logger.info(f"[build] добавлено в коллекцию: {cfg.collection} (persist={cfg.persist_dir})")

def search(q: str, k: int, fmt: str, cfg: Settings) -> None:
    """Семантический поиск: q → embed → NN → render."""
    emb = get_embedder(cfg)
    qvec = emb.encode([q], batch_size=1)[0]
    store = ChromaStore(ChromaConfig(persist_dir=cfg.persist_dir, collection=cfg.collection))
    hits: List[QueryHit] = store.query(qvec, k=k, where={})

    if fmt == "pretty":
        pretty(q, hits)
    elif fmt == "jsonl":
        print(jsonl(hits))
    elif fmt == "tsv":
        print(tsv(hits))
    else:
        raise ValueError(f"Unknown format: {fmt}")

def main() -> None:
    """CLI-аргументы и диспетчеризация команд."""
    cfg = Settings()
    ap = argparse.ArgumentParser(description="src (commented): семантический поиск без LLM")
    sub = ap.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="Индексировать источник (ePub)")
    b.add_argument("--epub", type=str, required=True, help="Путь к .epub файлу")

    s = sub.add_parser("search", help="Поиск по индексу")
    s.add_argument("--q", type=str, required=True, help="Запрос")
    s.add_argument("--k", type=int, default=6, help="Сколько результатов")
    s.add_argument("--format", type=str, default="pretty", choices=["pretty","jsonl","tsv"], help="Формат вывода")

    args = ap.parse_args()

    if args.cmd == "build":
        build_epub(args.epub, cfg)
    elif args.cmd == "search":
        search(args.q, args.k, args.format, cfg)
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
