import logging
from pathlib import Path

def set_logger(log_path, level=logging.INFO, stream=False):
    """
    Sets the logger to log info in terminal and file `log_path`.
    In general, it is useful to have a logger so that every output to the terminal is saved
    in a permanent file.
    Example:
    ```
    logging.info("Starting training...")
    ```
    Args:
        log_path: (string) where to log
        level: (int) the logging level
    """


    # def msg(self, message, *args, **kws):
    #     if self.isEnabledFor(level):
    #         self._log(level, message, args, **kws)

    # logging.Logger.msg = msg

    # # set up my own level
    logger = logging.getLogger()
    logger.setLevel(level)

    # remove existing handlers
    logger.handlers = []

    # if stream:
    #     # Logging to console
    #     stream_handler = logging.StreamHandler()
    #     stream_handler.addFilter(MaxLevelFilter(MSG_LEVEL))
    #     logger.addHandler(stream_handler)

    # os.path.isdir(os.path.dirname(log_path))
    # Logging to a file
    if log_path and Path(log_path).parent.is_dir():
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
        )
        file_handler.setLevel(level)  # file handler always debug level logging
        logger.addHandler(file_handler)


    return logger

# # Basic strategy
# import logging

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     filename='my_script.log',
#     filemode='w'
# )

# # Create a custom logger for the script
# logger = logging.getLogger(__name__)

# # Log some messages
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
