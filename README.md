# rag_searchkit (commented)
Модульный фреймворк для **семантического поиска LLM**.

## Архитектура
Источник → Парсер → Чанкер → Эмбеддер → Векторная БД → Поиск/Рендер

## Запуск
```bash
python3 -m venv .venv_llm
source ./.venv_llm/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```bash
python3 -m venv .venv_llm
source ./.venv_llm/bin/activate
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
pip install -r requirements.txt
```

```bash
python app.py build --epub "Upgrading and Repairing PCs.epub"
python app.py search --q "clear CMOS" --k 8 --format pretty
```
