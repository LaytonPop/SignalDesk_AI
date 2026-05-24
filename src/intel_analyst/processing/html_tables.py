"""
HTML 表格提取工具。

extract_tables_from_html(): 用 pandas.read_html() 解析 HTML 中的表格，
将每个表格保存为 CSV 到 data/tables/{source_name}/ 目录，
同时生成 ExtractedTable 记录（含行列数、CSV 路径、前 5 行预览）。

被 GenericNewsCrawler._fetch_article() 调用。
"""

from dataclasses import dataclass
from pathlib import Path
from re import sub

import pandas as pd

from intel_analyst.core.config import get_settings
from intel_analyst.schemas.article import ExtractedTable


@dataclass
class TableExtractionResult:
    tables: list[ExtractedTable]
    table_paths: list[str]


def extract_tables_from_html(html: str, source_name: str, article_title: str) -> TableExtractionResult:
    settings = get_settings()
    tables: list[ExtractedTable] = []
    table_paths: list[str] = []

    try:
        dataframes = pd.read_html(html)
    except ValueError:
        return TableExtractionResult(tables=[], table_paths=[])

    slug = _slugify(article_title)
    source_dir = settings.table_data_dir / source_name
    source_dir.mkdir(parents=True, exist_ok=True)

    for index, dataframe in enumerate(dataframes, start=1):
        csv_path = source_dir / f"{slug}_table_{index}.csv"
        dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")
        preview = dataframe.head(5).fillna("").to_dict(orient="records")
        tables.append(
            ExtractedTable(
                index=index,
                csv_path=str(csv_path),
                json_preview=preview,
                row_count=len(dataframe.index),
                column_count=len(dataframe.columns),
            )
        )
        table_paths.append(str(csv_path))

    return TableExtractionResult(tables=tables, table_paths=table_paths)


def _slugify(value: str) -> str:
    """将文章标题转为安全的文件名片段，去除非字母数字、截断到 80 字符。"""
    clean = sub(r"[^\w\-]+", "_", value.strip().lower())
    return clean[:80] or "article"
