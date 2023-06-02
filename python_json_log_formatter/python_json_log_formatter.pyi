from typing import Dict, List, Optional

VERSION: str

class PythonLogger:
    @classmethod
    def setup_logger(cls, version_constant: str, app: Optional[str], extra_context_dict: Optional[Dict[str, str]] = ..., logging_level: int = ..., disable_log_formatting: Optional[bool] = ...) -> None: ...
