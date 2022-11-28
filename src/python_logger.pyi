from logging import Filter, LogRecord
from typing import Dict, Optional

VERSION: str

class PythonLogger:
    @classmethod
    def setup_logger(cls, version_constant: str, app: str, extra_context_dict: Optional[Dict[str, str]] = ..., logging_level: int = ...) -> None: ...
    @classmethod
    def update_context(cls, context: Dict[str, str]) -> None: ...

class _ContextFilter(Filter):
    def __init__(self, context: Dict[str, str]) -> None: ...
    def update_context(self, context: Dict[str, str]) -> None: ...
    def filter(self, record: LogRecord) -> bool: ...
