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
from logging import CRITICAL, ERROR, LogRecord, Filter, WARNING, getLevelName, getLogger
from pathlib import Path
import traceback
from typing import Any, Dict, Mapping
from os import getenv, getcwd

LOGGER = getLogger(__name__)

class ContextFilter(Filter):
    """
    This is a filter which transforms log lines with metadata into structured JSON log lines.
    These structured JSON log lines are automatically parsed and indexed by LogDNA.
    """

    __job_retry_limit_env = "JOB_RETRY_LIMIT"
    """ENV-Key of the retry limit per job, name defined by Code Engine"""

    __job_retry_count_env = "JOB_INDEX_RETRY_COUNT"
    """ENV-Key of the current re-try count per job, name defined by Code Engine"""

    __job_remaining_retries = "job_remaining_retries"
    """ENV-Key of the current remaining job-retries, calculated during filter option, name defined here by developer."""

    __included_env_vars = [
            "ENVIRONMENT",
            "env",
            "JOB_INDEX",
            __job_retry_count_env,
            "JOB_MODE",
            __job_retry_limit_env,
            "CE_DOMAIN",
            "CE_JOB",
            "CE_JOBRUN",
            "CE_SUBDOMAIN",
            "HOSTNAME"
        ]

    def __init__(self, context: Dict[str, str]) -> None:
        super().__init__()
        self.__context: Dict[str, str] = {}
        self.update_context(context)

    def __add_env_variables(self, context_dict: Mapping[str, str]) -> Dict[str, Any]:
        """Creates a union of the existing context data and included environment variables.

        The result will be a new dictionary containing both keys,
        If a key exists in both the context and the env, the context has higher priority.
        A warning will be issued.

        Args:
            context_dict (Mapping[str, str]): Current logging context

        Returns:
            Dict[str, Any]: Merged Dict of logging context and certain env variables
        """

        # create a copy of the immutable object
        new_dict: Dict[str, Any] = dict(context_dict)

        for env_key in self.__included_env_vars:
            env_value = getenv(env_key, None)

            if env_value:
                if env_key in context_dict:
                    # skip pre-set keys, as user input is more important than env vars
                    # no real option of logging?
                    LOGGER.warning(f"Context key {env_key} set by both user and automatic env detection, skipping env value.")
                    continue
                new_dict[env_key] = env_value
        return new_dict

    def __calculate_remaining_job_retries(self) -> Dict[str, Any]:
        """Calculates the remaining job retries count for this job and adds them to the logging context.

        Requires the current retry count and the maximum limit saved in the environment.
        If not available, will log an warning.

        Saves the remaining retries count into the key `job_remaining_retries`.

        Returns:
            Dict[str, Any]: logging context containing only the remaining retries
        """
        new_dict: Dict[str, Any] = {}
        try:

            job_retry_count_str = getenv(self.__job_retry_count_env, None)
            job_retry_count_max_str = getenv(self.__job_retry_limit_env, None)
            if job_retry_count_str and job_retry_count_max_str:
                job_retry_count = int(job_retry_count_str)
                job_retry_count_max = int(job_retry_count_max_str)
                remaining_retries = str(job_retry_count_max - job_retry_count)

                new_dict[self.__job_remaining_retries] = remaining_retries
        except Exception as ex:
            # impossible to calculate
            LOGGER.warning("Impossible to calculate remaining job retries due to error", exc_info=ex)

        return new_dict

    def update_context(self, new_context_dict: Mapping[str, str]) -> None:
        """Updates the static saved context with new logging context, applying additional data on the way.

        The static context will be updated with the env variables and the calculated remaining job retries if available.
        Includes environment variables, where keys from `new_context_dict` take precedence, overwriting env vars.
        Will issue warnings if something calculated is not available or duplicate keys exists.
        Existing remaining job retries will be overwritten.

        This static context will then applied onto every logging line.

        Args:
            context (Dict[str, str]): New logging context to be applied as static context
        """

        new_dict = self.__add_env_variables(new_context_dict)

        job_retries_context = self.__calculate_remaining_job_retries()
        new_dict.update(job_retries_context)

        self.__context.update(new_dict)

    def __add_log_basic_info(self, record: LogRecord) -> Dict[str, Any]:
        """Extracts log record information into a logging dict context.

        Used for transferring certain required information into the new logging context to avoid loosing this data.

        Args:
            new_record_dict (Dict[str, Any]): The new context which will receive the existing data, overwriting existing entries.
            old_record (LogRecord): old context of the log
        """
        new_dict: Dict[str, Any] = {}

        # add exec info to the message if available
        message = record.msg
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info

            exc_info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = message + '\n' + exc_info
        new_dict['message'] = message

        # Append line number and path to log message
        new_dict['lineno'] = record.lineno
        new_dict['pathname'] = record.pathname

        # Add existing metadata to the new record message
        if isinstance(record.args, dict):
            for k, v in record.args.items():
                new_dict[k] = v

        return new_dict

    def __check_is_imported_module(self, path_name: str) -> bool:
        work_dir = Path(getcwd())
        log_path = Path(path_name)

        # from python 3.9 the main module should always be absolute, but sometimes it is not somehow.
        # make sure the path is absolute
        if not log_path.is_absolute():
            log_path = log_path.resolve()

        # if the module is located within the work dir it is actually code from this program
        # other code is installed directly within the /opt/app-root/lib64/python3.9/site-packages/
        if not log_path.is_relative_to(work_dir):
            return True

        # also verify it is not inside the venv dir
        if "venv" in path_name:
            return True

        return False

    def __filter_imported_modules(self, record: LogRecord) -> Dict[str, Any]:
        """Filters errors and critical failures from dependencies and sets their level to max warning.

        Will change the level of the record via side effects if filtered.

        Args:
            old_record (LogRecord): the log record being filtered.
        """

        new_dict: Dict[str, Any] = {}

        try:
            # debug, info and warning can stay in any case
            if record.levelno < ERROR:
                return new_dict

            # this is not a imported module, leave it as it is
            if not self.__check_is_imported_module(record.pathname):
                return new_dict

            ###
            # the code is for sure from a requirement/sub-module and thus should be changed
            ###

            # save the old level
            new_dict["original_levelno"] = record.levelno
            new_dict["original_levelname"] = record.levelname

            # set all error/critical to warning
            record.levelno = WARNING
            record.levelname = getLevelName(WARNING)
            new_dict["filter_imported_modules"] = "Filtered"

        except Exception as ex:
            new_dict["filter_imported_modules"] = "Failed: " + str(ex)

        return new_dict

    def __check_failed_pipeline_status(self, record: LogRecord) -> Dict[str, Any]:

        new_dict: Dict[str, Any] = {}
        # Handle error logs
        # 40: Error, and higher (critical)
        if record.levelno >= CRITICAL:
            new_dict['job_status'] = 'failed'
            new_dict['pipeline_status'] = 'failed'

        return new_dict

    def filter(self, record: LogRecord) -> bool:
        """Combine message and contextual information into message argument of the record."""

        # start with the pre-set context
        new_record_msg: Dict[str, Any] = self.__context.copy()

        new_dict = self.__filter_imported_modules(record)
        new_record_msg.update(new_dict)

        new_dict = self.__add_log_basic_info(record)
        new_record_msg.update(new_dict)

        new_dict = self.__check_failed_pipeline_status(record)
        new_record_msg.update(new_dict)

        new_dict = self.__add_log_basic_info(record)
        new_record_msg.update(new_dict)

        # Override record message and clear record args
        record.msg = json.dumps(new_record_msg)
        record.args = {}

        return True
