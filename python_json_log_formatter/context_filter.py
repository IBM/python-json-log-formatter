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
from logging import LogRecord, Filter, WARNING, getLevelName
from pathlib import Path
import traceback
from typing import Any, Dict
from os import getenv, getcwd

class ContextFilter(Filter):
    """
    This is a filter which transforms log lines with metadata into structured JSON log lines.
    These structured JSON log lines are automatically parsed and indexed by LogDNA.
    """

    def __init__(self, context: Dict[str, str]) -> None:
        super().__init__()
        self.__context: Dict[str, str] = {}
        self.update_context(context)

    def update_context(self, context: Dict[str, str]) -> None:
        env_vars = [
            "ENVIRONMENT",
            "JOB_INDEX",
            "JOB_INDEX_RETRY_COUNT",
            "JOB_MODE",
            "JOB_RETRY_LIMIT",
            "CE_DOMAIN",
            "CE_JOB",
            "CE_JOBRUN",
            "CE_SUBDOMAIN",
            "HOSTNAME"
        ]

        for env_var in env_vars:
            var_val = getenv(env_var, None)

            if var_val:
                self.__context[env_var] = var_val

        # calculate remaining job retries
        try:

            job_retry_count_str = getenv("JOB_INDEX_RETRY_COUNT", None)
            job_retry_count_max_str = getenv("JOB_RETRY_LIMIT", None)
            if job_retry_count_str and job_retry_count_max_str:
                job_retry_count = int(job_retry_count_str)
                job_retry_count_max = int(job_retry_count_max_str)
                remaining_retries = str(job_retry_count_max - job_retry_count)

                self.__context["job_remaining_retries"] = remaining_retries
        except Exception:
            # impossible to calculate
            # this is a antipattern, but this does not need to be logged
            pass


        self.__context.update(context)

    def __add_existing_info(self, new_record_dict: Dict[str, Any], old_record: LogRecord):
        # Append line number, path and level to log message
        new_record_dict['message'] = old_record.msg
        new_record_dict['lineno'] = old_record.lineno
        new_record_dict['pathname'] = old_record.pathname
        new_record_dict['level'] = old_record.levelname

        # Add existing metadata to the new record message
        if isinstance(old_record.args, dict):
            for k, v in old_record.args.items():
                new_record_dict[k] = v


    def __add_context_info(self, new_record_dict: Dict[str, Any]) -> None:
        # Add contextual information to the record message
        for arg_name, value in self.__context.items():
            new_record_dict[arg_name] = value

    def __add_available_exec_info(self, new_record_dict: Dict[str, Any], old_record: LogRecord):
        if old_record.exc_info:
            exc_type, exc_value, exc_traceback = old_record.exc_info

            exc_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            new_record_dict['message'] = str(new_record_dict['message']) + '\n' + exc_info

            # Clear record.exc_info
            old_record.exc_info = None

    def __filter_imported_modules(self, new_record_dict: Dict[str, Any], record: LogRecord):
        """Filters errors and critical failures from dependencies and sets their level to max warning.

        Args:
            old_record (LogRecord): the log record being filtered.
        """
        try:
            # debug, info and warning can stay
            if record.levelno < 40:
                return

            # if the module is located within the workdir it is actually code from this program
            # other code is installed directly within the /opt/app-root/lib64/python3.9/site-packages/
            workdir = Path(getcwd())
            log_path = Path(record.pathname)
            # However, the venv directory needs also to be ignored
            if log_path.is_relative_to(workdir) and "venv" not in record.pathname:
                # this is module code which should be able to send error/critical messages
                return

            # save the old level
            new_record_dict["original_levelno"] = record.levelno
            new_record_dict["original_levelname"] = record.levelname

            # set all error/critical to warning
            record.levelno = WARNING
            record.levelname = getLevelName(WARNING)

            new_record_dict["filter_imported_modules"] = "true"

        except Exception as ex:
            new_record_dict["filter_imported_modules"] = "Failed: " + str(ex)

    def __check_failed_pipeline_status(self, new_record_dict: Dict[str, Any], old_record: LogRecord):
        # Handle error logs
        # 40: Error, and higher (critical)
        if old_record.levelno >= 40:
            new_record_dict['job_status'] = 'failed'
            new_record_dict['pipeline_status'] = 'failed'

    def filter(self, record: LogRecord) -> bool:
        """Combine message and contextual information into message argument of the record."""
        new_record_msg: Dict[str, Any] = {}

        self.__filter_imported_modules(new_record_msg, record)
        self.__add_existing_info(new_record_msg, record)

        self.__add_context_info(new_record_msg)

        self.__check_failed_pipeline_status(new_record_msg, record)

        # Add exception info to log message
        self.__add_available_exec_info(new_record_msg, record)

        # Override record message and clear record args
        record.msg = json.dumps(new_record_msg)
        record.args = {}

        return True
