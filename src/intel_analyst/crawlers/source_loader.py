"""
站点配置加载器 —— 从 JSON 文件反序列化为 SourceConfig。

相对路径会基于项目根目录（ROOT_DIR）解析。
被 CrawlerService.crawl() 调用。
"""

import json
from pathlib import Path

from intel_analyst.core.config import get_settings
from intel_analyst.schemas.source import SourceConfig


class SourceLoader:
    def __init__(self) -> None:
        self.settings = get_settings()

    def load(self, source_path: str) -> SourceConfig:
        path = Path(source_path)
        if not path.is_absolute():
            path = self.settings.root_dir / source_path
        data = json.loads(path.read_text(encoding="utf-8"))
        return SourceConfig.model_validate(data)
