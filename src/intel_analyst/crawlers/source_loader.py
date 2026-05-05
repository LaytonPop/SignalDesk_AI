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
