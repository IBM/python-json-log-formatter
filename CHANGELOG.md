# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Python-Logger [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Fixed

### Known Issues

## Python-Logger [3.3.2] - 2023-10-31

### Fixed

* Increases default split size from 1000 to 3000
* Fixes not printing the original message on exception, but only the stack trace

## Python-Logger [3.3.1] - 2023-10-26

### Fixed

* Switch back the message key from `msg` to `message` as this keyword is required

## Python-Logger [3.3.0] - 2023-10-25

### Changed

* Exception traces will be logged as new log messages with the very same attributes instead of contacting them into a single message

### Fixed

* Overly long log messages will be split into multiple smaller log messages if they exceed a set threshold
  * Adds new optional argument `split_threshold` with a default of 1000

## Python-Logger [3.2.5] - 2023-07-10

### Changed

* Changing `msg` back to `message` to allow the logging tool to detect it

## Python-Logger [3.2.4] - 2023-07-10

### Changed

* Trying to modify the original record as few as possible, as that can have unintended side consequences
  * No longer removes the record args or exec info from it
* The place where the message is saved is changed from `message` to `msg`, to stay in the same naming as the original record would
  * Can be changed via a central variable, changing it everywhere

## Python-Logger [3.2.3] - 2023-06-02

### Changed

* Wraps the whole `filter` method in a try-catch block
  * Avoid issues stopping the program due to a logger issue

### Fixed

* Removed `msg` attribute as it is a duplicate of `message`

## Python-Logger [3.2.2] - 2023-06-02

### Added

* Method docs
* Dockerfile for testing
  * Added a `.dockerignore` file
*

### Changed

* Moved the code to add the exc_info into an individual method
* renamed private method `__add_env_variables` to `__add_selected_env_vars_to_context`

### Fixed

* Log levels show up again in the logging analyzer tool
  * added `new_dict["level"] = record.levelname` to the log output

## Python-Logger [3.2.1] - 2023-06-01

### Added

* The logger now also logs the version of the logger itself.

### Changed

* The version string is now in a file named `_version.py`, similar to other Python projects
  * Adjusted file paths and build method for this change

## Python-Logger [3.2.0] - 2023-05-23

### Added

* Added option to disable the log formatting for local development
  * Either supply `disable_log_formatting=True` when initializing the logger
  * Or supply the ENV attribute `DISABLE_LOG_FORMATTING=True`
  * Will only check for ENV if it is not explicitly set to false
* The logger includes all Logging-Record attributes by default
  * Added an option to exclude individual fields, using the new attribute `excluded_logging_context_keys`
  * No keys are excluded by default

### Changed

* The logger will set the `pipeline_status=failed` only if an error is critical, as regular errors must not mean a failure.

### Fixed

* Added missing bracket in log format string

## Python-Logger [3.1.0] - 2023-05-22

### Added

* Full Method documentation
* Testing file to execute the logger as stand-alone

### Changed

* Refactored the whole `context_filter` module to split up complex methods into smaller ones

## Python-Logger [3.0.2] - 2023-01-21

### Added

* added `env` to the default env import

### Fixed

* Missing comma, fixing `env` and `JOB_INDEX` default included variables

## Python-Logger [3.0.1] - 2022-12-21

### Fixed

* Log errors if the main module was called directly/relative call.

## Python-Logger [3.0.0] - 2022-12-13

### Added

* Includes a lot of env vars in the logging automatically
* Calculates the remaining job-restarts
* Submodule error and critical level is set to warning
* Finally working typing

### Changed

* Changed module name from `python_logger` to `python-json-log-formatter` to match import name
* Makes the date in the version string optional to support dynamic version imports in the build process
* Moved a lot of code into individual functions for readability
* Build version determined automatically from the python code

## Python-Logger [2.0.4] - 2022-12-09

### Changed

* re-added the stub files in hope of fixing typing

## Python-Logger [2.0.3] - 2022-12-09

### Added

* py.typed file for supporting typing
* added automatic dependabot version upgrades

### Changed

* removed old stub files as the typing is included within the python files themselves
* Upgraded python deploy action from v3 to v4

## Python-Logger [2.0.2] - 2022-11-28

### Added

* Support for later changing of the context dictionary if the information is not available from the start

### Changed

* Set inner ContextFilter to protected

## Python-Logger [2.0.1] - 2022-11-28

* Jumped due to an error in the version control

## Python-Logger [2.0.0] - 2022-11-28

### Added

* Type stub file

### Changed

* Requires `app` parameter and allows for an additional context dictionary to be supplied
* Uses python3.9 instead of python3.10 for better compatibility.

### Fixed

* Every logging uses the hardcoded `etl_query_generator` as the name. It's free now.

### Known Issues

## Python-Logger [1.0.2] - 2022-11-25

### Added

Release Workflow

## Python-Logger [1.0.1] - 2022-11-24

### Added

Release on PyPi

## Python-Logger [1.0.0] - 2022-11-24

### Added

The initial release of the python logging module
