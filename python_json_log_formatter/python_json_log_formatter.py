"""
 ----------------------------------------------------------------------------------------------
# Copyright 2022 IBM All Rights Reserved.
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
from distutils.util import strtobool

from logging import INFO, StreamHandler, basicConfig
from os import getenv
import re
from typing import ClassVar

from python_json_log_formatter.context_filter import ContextFilter, MESSAGE_KEY_CONST
from python_json_log_formatter._version import __version__


class PythonLogger:
    """This class wraps functions used for logging for an easier, direct access.

    Methods:
        setup_logger - Configures the root as required. To be called before any logging commands in the main file (very top).
        update_context -

    Raises:
        ValueError: _description_
    """

    __context_filter: ClassVar[ContextFilter]

    @property
    def message_key(self) -> str:
        if self.__context_filter:
            return self.__context_filter.message_key
        else:
            return MESSAGE_KEY_CONST

    @property
    def excluded_logging_context_keys(self) -> list[str]:
        """Keys of the logging Record which should not be included automatically."""
        return self.__context_filter.excluded_logging_context_keys

    @excluded_logging_context_keys.setter
    def excluded_logging_context_keys(self, value: list[str]) -> None:
        self.__context_filter.excluded_logging_context_keys = value

    @classmethod
    def setup_logger(
        cls,
        version_constant: str,
        app: str | None,
        extra_context_dict: dict[str, str] | None = None,
        logging_level: int = INFO,
        disable_log_formatting: bool | None = None,
        split_threshold: int = 3000,
        ex_trace_as_new_message: bool | None = None,
        log_format_str: str | None = None,
    ) -> None:
        """Configures the root as required. To be called before any logging commands in the main file (very top).

        Sets the logging format for the root logger and thus for every child logger.
        In EVERY file where logging happens, please use `LOGGER = logging.getLogger(__name__)` to get an individual logger.
        Allows to print exception information on any logging level, not only exception and higher.
        Supply exec_info to print these.

        Sets pipeline status to failed on ERROR or CRITICAL, supports minor logging levels (41, etc).

        Args:
            version_constant (str): Program version, requires semantic version format '1.0.0' with a prefix '(yyyy/mm/dd)'
            app (str): Name of the app for the logger.
            extra_context_dict (Dict[str, str]): additional logging information like 'env', 'processing_id' and more.
            logging_level (int): Log level of root logger. Defaults to INFO.
            disable_log_formatting (bool, optional): Disable the log formatting, e.g. local development. Defaults to None/False.
            split_threshold (int): Splits the message after a certain length into a new message with the same attributes. Defaults to 3000.
            ex_trace_as_new_message (bool, optional): Split exception stack traces into individual messages, instead of concatenating them into a single long one. Defaults to None/False.

        Raises:
            ValueError: Incorrect version format supplied
        """

        # check that the version string has the correct format
        version_match = re.fullmatch(
            r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?(\s+\(\d{4}/\d{2}/\d{2}\))?$",
            version_constant,
        )
        if not version_match:
            raise ValueError(
                "Incorrect version format. Please use semantic versioning and prepend optionally '(yyyy/mm/dd)':https://semver.org/#semantic-versioning-specification-semver  https://ihateregex.io/expr/semver/"
            )

        if disable_log_formatting is None:
            disable_log_formatting = bool(
                strtobool(getenv("DISABLE_LOG_FORMATTING", "False"))
            )

        if ex_trace_as_new_message is None:
            ex_trace_as_new_message = bool(
                strtobool(getenv("EX_TRACE_AS_NEW_MESSAGE", "False"))
            )

        handler = StreamHandler()

        context_dict = extra_context_dict or {}
        if app:
            context_dict["app"] = app
        context_dict["version"] = version_constant
        context_dict["logger_version"] = __version__
        cls.__context_filter = ContextFilter(
            context_dict,
            disable_log_formatting,
            split_threshold,
            ex_trace_as_new_message,
        )
        handler.addFilter(cls.__context_filter)
        basicConfig(
            level=logging_level,
            format=log_format_str  # custom provided
            or f"%({cls.__context_filter.message_key})s",
            handlers=[handler],
        )

    @classmethod
    def update_context(cls, context: dict[str, str]) -> None:
        """Updates additional context information added to each log line.

        Will update the existing context with the given one, overwriting existing keys.
        Existing keys without a new match will not be deleted

        Args:
            context (Dict[str, str]): context information to be included in each log line
        """
        cls.__context_filter.update_context(context)
