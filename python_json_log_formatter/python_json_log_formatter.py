"""
 ----------------------------------------------------------------------------------------------
# Copyright 2019 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 ----------------------------------------------------------------------------------------------
SPDX-License-Identifier: Apache-2.0

Description:
 Provides default logging config for python logging.

Repository:
  https://github.com/IBM/python_json_log_formatter

Author:
 Niels Korschinsky
"""

from __future__ import annotations


import json
from logging import INFO, LogRecord, Filter, StreamHandler, basicConfig
import re
import traceback
from typing import Any, ClassVar, Dict, Optional


VERSION = "3.0.0"

class PythonLogger:

    __context_filter: ClassVar[_ContextFilter]

    @classmethod
    def setup_logger(cls,
                     version_constant: str,
                     app: str,
                     extra_context_dict: Optional[Dict[str, str]] = None,
                     logging_level: int = INFO) -> None:
        """Setups the root logger of the system. To be called before any logging commands in the main file (very top).

        Sets the logging format for the root logger and thus for every child logger.
        In EVERY file where logging happens, please use `LOGGER = logging.getLogger(__name__)` to get an individual logger.
        Allows to print exception information on any logging level, not only exception and higher.
        Supply exec_info to print these.

        Sets pipeline status to failed on ERROR or CRITICAL, supports minor logging levels (41, etc).

        Args:
            version_constant (str): Program version, requires semantic version format '1.0.0' with a prefix '(yyyy/mm/dd)'
            app (str): Name of the app for the logger, mandatory for the context
            extra_context_dict (Dict[str, str]): additional logging information like 'env', 'processing_id' and more.
            logging_level (int, optional): Log level of root logger. Defaults to INFO.

        Raises:
            ValueError: Incorrect version format supplied
        """

        version_match = re.fullmatch(
                r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?\s+(\(\d{4}/\d{2}/\d{2}\))$",
                version_constant)
        if not version_match:
            raise ValueError("Incorrect version format. Please use semantic versioning and prepend '(yyyy/mm/dd)':https://semver.org/#semantic-versioning-specification-semver  https://ihateregex.io/expr/semver/")

        handler = StreamHandler()

        context_dict = extra_context_dict or {}
        context_dict["app"] = app
        context_dict["version"] = version_constant
        cls.__context_filter =_ContextFilter(context_dict)
        handler.addFilter(cls.__context_filter)
        basicConfig(
            level=logging_level,
            format="%(asctime)s %(name)s] %(levelname)s: %(message)s",
            handlers=[handler]
    )

    @classmethod
    def update_context(cls, context: Dict[str, str]) -> None:
        cls.__context_filter.update_context(context)

class _ContextFilter(Filter):
    """
    This is a filter which transforms log lines with metadata into structured JSON log lines.
    These structured JSON log lines are automatically parsed and indexed by LogDNA.
    """

    def __init__(self, context: Dict[str, str]) -> None:
        super().__init__()
        self.__context: Dict[str, str] = context

    def update_context(self, context: Dict[str, str]) -> None:
        self.__context.update(context)

    def filter(self, record: LogRecord) -> bool:
        """Combine message and contextual information into message argument of the record."""
        new_record_msg: Dict[str, Any] = {
            "message": record.msg
        }

        # Add contextual information to the record message
        for k, v in self.__context.items():
            new_record_msg[k] = v

        # Add given metadata to the record message
        if isinstance(record.args, dict):
            for k, v in record.args.items():
                new_record_msg[k] = v

        # Handle error logs
        # 40: Error, and higher (critical)
        if record.levelno >= 40:
            new_record_msg['job_status'] = 'failed'
            new_record_msg['pipeline_status'] = 'failed'

        # Add exception info to log message
        # Only set if it is an exception
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info

            exc_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            new_record_msg['message'] = str(new_record_msg['message']) + '\n' + exc_info

            # Clear record.exc_info
            record.exc_info = None

        # Append line number, path and level to log message
        new_record_msg['lineno'] = record.lineno
        new_record_msg['pathname'] = record.pathname
        new_record_msg['level'] = record.levelname

        # Override record message and clear record args
        record.msg = json.dumps(new_record_msg)
        record.args = {}

        return True