
from logging import getLogger

from python_json_log_formatter.python_json_log_formatter import PythonLogger, VERSION

if __name__ == '__main__':

    PythonLogger.setup_logger(
        version_constant=VERSION,
        app="python_json_log_formatter"
    )


    # special logger
    LOGGER = getLogger(__name__)

    LOGGER.info("test", extra={"test": "testval1"})

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
