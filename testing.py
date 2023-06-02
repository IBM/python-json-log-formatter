
from logging import getLogger

from python_json_log_formatter.python_json_log_formatter import PythonLogger
from python_json_log_formatter._version import __version__

if __name__ == '__main__':

    PythonLogger.setup_logger(
        version_constant=__version__,
        app="python_json_log_formatter"
    )


    # special logger
    LOGGER = getLogger(__name__)

    LOGGER.info("test", extra={"test": "testval1"})
    LOGGER.info("test", {"test": "testval1"})

    PythonLogger.update_context(
        {
            "SOURCE_BRANCH": "test",
            "TARGET_BRANCH": "test2"
        }
    )


    LOGGER.error("error-test", extra={"test2": "testval_2"})
    try:
        raise ValueError("testError")
    except Exception as ex:
        LOGGER.critical("CRITICAL FAILURE: Completely aborted: Failed to execute.", exc_info=ex)
