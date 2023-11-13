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
from logging import CRITICAL, ERROR, LogRecord, Filter, WARNING, Logger, getLevelName, getLogger, makeLogRecord
from pathlib import Path
import traceback
from typing import Any, ClassVar, Dict, List, Mapping
from os import getenv, getcwd

LOGGER: Logger = getLogger(__name__)

class _StopLogging(Exception):
    pass

class ContextFilter(Filter):
    """
    This is a filter which transforms log lines with metadata into structured JSON log lines.
    These structured JSON log lines are automatically parsed and indexed by LogDNA.
    """

    @property
    def message_key(self):
        return self.__message_key

    __message_key: ClassVar[str] = "message"
    """name of the key under which the msg will be saved"""

    __part_key: ClassVar[str] = "part_nr"
    """number of the current part of an original message"""

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
            "HOSTNAME",
            "BRANCH_NAME",
            "TARGET_BRANCH_NAME"
        ]
    """Keys of the environment which should be included by default"""

    @property
    def excluded_logging_context_keys(self) -> List[str]:
        """Keys of the logging Record which should not be included automatically."""
        return self.__excluded_logging_context_keys

    @excluded_logging_context_keys.setter
    def excluded_logging_context_keys(self, value: List[str]) -> None:
        self.__excluded_logging_context_keys = value

    __excluded_logging_context_keys: List[str] = [

    ]
    """Keys of the logging Record which should not be included automatically."""

    def __init__(self,
                 context: Dict[str, str],
                 disable_log_formatting: bool = False,
                 split_threshold: int = 1000,
                 ex_trace_as_new_message: bool = False) -> None:
        super().__init__()
        self.__disable_log_formatting = disable_log_formatting
        self.__context: Dict[str, str] = {}
        self.__split_threshold = split_threshold
        self.__ex_trace_as_new_message = ex_trace_as_new_message
        self.update_context(context)

    def __add_selected_env_vars_to_context(self, context_dict: Mapping[str, str]) -> Dict[str, Any]:
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

        new_dict = self.__add_selected_env_vars_to_context(new_context_dict)

        job_retries_context = self.__calculate_remaining_job_retries()
        new_dict.update(job_retries_context)

        self.__context.update(new_dict)

    def __add_log_record_info(self, record: LogRecord) -> Dict[str, Any]:
        """Extracts log record information into a new logging dict context.

        Used for transferring certain required information into the new logging context to avoid loosing this data.

        Args:
            record (LogRecord): the log record which contents will be transferred

        Returns:
            Dict[str, Any]: Dict with context information to be merged into other context information
        """

        # add all available attributes of the record
        # copy to ensure to not edit the record itself
        new_dict: Dict[str, Any] = record.__dict__.copy()

        for key in self.__excluded_logging_context_keys:
            new_dict.pop(key, None)

        # without specifying this level, the logging service cannot detect its level
        # so this is super important
        new_dict["level"] = record.levelname
        new_dict[self.__message_key] = record.msg

        if self.__message_key != "msg":
            # remove msg as it is saved in another name
            # message is used in the formatting string
            new_dict.pop("msg", None)

        # Add arguments individual to the new record message
        if isinstance(record.args, dict):
            for k, v in record.args.items():
                new_dict[k] = v

            # set them to empty, as already included
            #record.args = {}
            # Edit: do not remove it, as the record should be left as intact as possible

            # remove it from the new_dict, as they are saved individually
            new_dict.pop("args", None)

        return new_dict

    def __log_available_exec_info(self, new_record_dict: Dict[str, Any], record: LogRecord):
        """Updates the provided context information with exc_information from the log record.

        Will remove the exc_info from the record.
        Updates the message of the context dict.

        Args:
            new_record_dict (Dict[str, Any]): Context dict with existing message and other information
            record (LogRecord): LogRecord with possible exc_info field
        """

        if record.exc_info:

            # get the individual parts
            exc_type, exc_value, exc_traceback = record.exc_info

            # only save the trace
            exc_info = traceback.format_exception(exc_type, exc_value, exc_traceback)

            # delete the info from the saved dict

            new_record_dict.pop("exc_info", None)
            # Clear record.exc_info
            record.exc_info = None

            if not self.__ex_trace_as_new_message:

                # append the exception stack to the existing message
                # add new lines
                old_msg = new_record_dict[self.__message_key]
                new_msg = old_msg + "\n" + "\n".join(exc_info)
                new_record_dict[self.__message_key] = new_msg
            else:
                # make a new log line for each stack trace element
                # starting with the original message, so it is send first

                # Log it now, so it is printed before the others
                # does not contain the exc_info, so it will go through
                new_record = makeLogRecord(new_record_dict)
                # pop the message to exclude it from further messages
                # also we need to assign it to "msg" so when handled
                # The filter can then do its thing
                msg = new_record_dict.pop(self.__message_key)
                new_record.msg = msg
                LOGGER.handle(new_record)

                # now log each line as a new log message
                # but exclude the already logged message
                # it is popped before
                for row in exc_info:
                    new_record = makeLogRecord(new_record_dict)
                    new_record.msg = row
                    LOGGER.handle(new_record)

                # stop the logging, the original message was sent first
                raise _StopLogging()

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
            # update possible already saved keys
            new_dict["levelno"] = record.levelno
            new_dict["levelname"] = record.levelname
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

    def __log_too_long_message(self, new_record_dict: Dict[str, Any]):
        if len(new_record_dict[self.__message_key]) <= self.__split_threshold:
            # that should be fine in length
            # must be smaller equals, only truncate after the threshold
            return

        # this is too long, split into multiple messages
        new_part_nr: int = new_record_dict.get(self.__part_key, 0)

        # log the remaining message as new log
        message: str = new_record_dict.pop(self.__message_key)

        old_index = 0
        while(old_index < len(message)):
            new_part_nr: int = new_part_nr + 1
            part_prefix = f"{new_part_nr}: "
            index = old_index + self.__split_threshold - len(part_prefix)

            # get that part of the message and send it
            part_msg = part_prefix + message[old_index:index]
            new_record = makeLogRecord(new_record_dict)
            new_record.msg = part_msg
            LOGGER.handle(new_record)
            old_index = index
            # now everything has been printed out

        raise _StopLogging()


    def filter(self, record: LogRecord) -> bool:
        """Combine message and contextual information into message argument of the record."""
        try:

            # start with the pre-set context
            new_record_msg: Dict[str, Any] = self.__context.copy()

            new_dict = self.__filter_imported_modules(record)
            new_record_msg.update(new_dict)

            new_dict = self.__add_log_record_info(record)
            new_record_msg.update(new_dict)

            new_dict = self.__check_failed_pipeline_status(record)
            new_record_msg.update(new_dict)

            # These now will log, therefore must be executed at the end
            self.__log_available_exec_info(new_record_msg, record)
            self.__log_too_long_message(new_record_msg)

            # Override record message and clear record args
            dumped_new_dict = json.dumps(new_record_msg)

            if not self.__disable_log_formatting:
                # Override record message and clear record args
                record.msg = dumped_new_dict
            else:
                # save it in new attribute, will not be shown.
                record.log_formatting_message = dumped_new_dict

        except _StopLogging:
            # this message has been fully logged
            return False
        except Exception:
            # ensure it does not stop the program if something does wrong
            # the message will still be logged
            return True

        return True