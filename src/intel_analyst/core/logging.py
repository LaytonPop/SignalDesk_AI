"""
日志初始化。

被 main.py 的 lifespan 在应用启动时调用一次。
dev 环境日志级别 DEBUG，其他环境 INFO。
"""

import logging


def configure_logging(app_env: str) -> None:
    level = logging.DEBUG if app_env == "dev" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
