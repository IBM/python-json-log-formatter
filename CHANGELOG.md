# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Python-Logger [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Fixed

### Known Issues

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
