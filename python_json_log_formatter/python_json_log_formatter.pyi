from typing import Dict, Optional

VERSION: str

class PythonLogger:
    @classmethod
    def setup_logger(cls, version_constant: str, app: str, extra_context_dict: Optional[Dict[str, str]] = ..., logging_level: int = ...) -> None: ...
    @classmethod
    def update_context(cls, context: Dict[str, str]) -> None: ...