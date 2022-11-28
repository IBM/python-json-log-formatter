from logging import Filter, LogRecord
from typing import Dict, Optional

VERSION: str

class PythonLogger:
    @staticmethod
    def setup_logger(version_constant: str, app: str, extra_context_dict: Optional[Dict[str, str]] = ..., logging_level: int = ...) -> None: ...

class ContextFilter(Filter):
    def __init__(self, context: Dict[str, str]) -> None: ...
    def set_context(self, context: Dict[str, str]) -> None: ...
    def filter(self, record: LogRecord) -> bool: ...