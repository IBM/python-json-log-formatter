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

__all__ = ["PythonLogger", "__version__"]

from python_json_log_formatter.python_json_log_formatter import (
    PythonLogger as PythonLogger,
)
from python_json_log_formatter._version import __version__ as __version__
from python_json_log_formatter.context_filter import (
    MESSAGE_KEY_CONST as MESSAGE_KEY_CONST,
)
