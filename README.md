# python-logger

<p align="center">
    <a href="https://github.com/IBM/python-json-log-formatter/blob/master/LICENSE" alt="Licence">
        <img src="https://img.shields.io/hexpm/l/apa" /></a>
    <a href="https://pypi.org/project/python-json-log-formatter/" alt="PyPi">
        <img src="https://img.shields.io/pypi/v/python-json-log-formatter" /></a>
    <a href="https://github.com/IBM/python-json-log-formatter/releases" alt="GitHub release (latest SemVer)">
        <img src="https://img.shields.io/github/v/release/IBM/python-json-log-formatter" /></a>
</p>

Supplements a default formatter configuration for machine-readable JSON logging and applies it.

This module should be included as a sub-module in python projects with logging.
Please avoid copy-pasting as no updates can be supplied that way.

## Usage

1. Install the module via the `requirements.txt` or per CLI: `pip install python-json-log-formatter`
2. Please include the `PythonLogger` module, using a `from module import class` statement.
3. After the imports, please declare a version constant. \
    This constant should use [semantic versioning](https://semver.org/#semantic-versioning-specification-semver), with a prepended date `(YYYY/MM/DD)`.\
    Other examples, without the date, can be found [here](https://ihateregex.io/expr/semver/)
4. Before any argument parsing or any other logging, the logger should be initialized
5. In **EVERY** file, the logger needs to be imported using `LOGGER = logging.getLogger(__name__)`

```python
from python_json_log_formatter import PythonLogger
import logging

VERSION = "1.0.0 (2022/11/24)"
PythonLogger.setup_logger(VERSION)

LOGGER = logging.getLogger(__name__)
```

Optionally, it is also possible to change the log level:

```python
from python_json_log_formatter import PythonLogger
import logging

VERSION = "1.0.0 (2022/11/24)"
PythonLogger.setup_logger(VERSION, logging.DEBUG)

LOGGER = logging.getLogger(__name__)
```

## Features

Sets the logging format for the root logger and thus for every child logger.
In EVERY file where logging happens, please use `LOGGER = logging.getLogger(__name__)` to get an individual logger.
Allows printing exception information on any logging level, not only on the `EXCEPTION` level but also for `INFO` or `DEBUG`.
Supply `exec_info` to print these.

Sets `pipeline_status` and `job_status` to `failed` on `CRITICAL`, supports minor logging levels (41, etc).

To disable the logging on local machines, supply `disable_log_formatting=True` when configuring the logger.
Alternatively, without code changes, you can supply the ENV var `DISABLE_LOG_FORMATTING"=True` to generally disable it.

Every attribute of the LogRecord will be included in the formatted message unless specified in the `excluded_logging_context_keys` list.
