from python_json_log_formatter.context_filter import ContextFilter as ContextFilter
from typing import Dict, List, Optional

VERSION: str

class PythonLogger:
    @property
    def excluded_logging_context_keys(self) -> List[str]: ...
    @excluded_logging_context_keys.setter
    def excluded_logging_context_keys(self, value: List[str]) -> None: ...
    @classmethod
    def setup_logger(cls, version_constant: str, app: Optional[str], extra_context_dict: Optional[Dict[str, str]] = ..., logging_level: int = ...) -> None: ...
    @classmethod
    def update_context(cls, context: Dict[str, str]) -> None: ...
