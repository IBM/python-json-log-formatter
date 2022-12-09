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

from logging import INFO, StreamHandler, basicConfig
import re
from typing import ClassVar, Dict, Optional

from python_json_log_formatter.context_filter import ContextFilter


VERSION = "3.0.0"

class PythonLogger:

    __context_filter: ClassVar[ContextFilter]

    @classmethod
    def setup_logger(cls,
                     version_constant: str,
                     app: Optional[str],
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
            app (str): Name of the app for the logger.
            extra_context_dict (Dict[str, str]): additional logging information like 'env', 'processing_id' and more.
            logging_level (int, optional): Log level of root logger. Defaults to INFO.

        Raises:
            ValueError: Incorrect version format supplied
        """

        version_match = re.fullmatch(
                r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?(\s+\(\d{4}/\d{2}/\d{2}\))?$",
                version_constant)
        if not version_match:
            raise ValueError("Incorrect version format. Please use semantic versioning and prepend '(yyyy/mm/dd)':https://semver.org/#semantic-versioning-specification-semver  https://ihateregex.io/expr/semver/")

        handler = StreamHandler()

        context_dict = extra_context_dict or {}
        if app:
            context_dict["app"] = app
        context_dict["version"] = version_constant
        cls.__context_filter = ContextFilter(context_dict)
        handler.addFilter(cls.__context_filter)
        basicConfig(
            level=logging_level,
            format="%(asctime)s %(name)s] %(levelname)s: %(message)s",
            handlers=[handler]
    )

    @classmethod
    def update_context(cls, context: Dict[str, str]) -> None:
        cls.__context_filter.update_context(context)