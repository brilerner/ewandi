import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

from utils.general import get_root

import logging


def set_test(file):
    print("file:", file)
    print("__name__:", __name__)
    print("__package__:", __package__)
    print("__file__:", __file__)


def setup_logging(filename, userid=None, level=logging.INFO, default_dir="logs", persistent_log=False):
    """
    Put the datetime in the log filename.
    """
    from datetime import datetime

    if persistent_log:
        datetime_str = datetime.now().strftime("%Y-%m-%d")
    else:
        datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    final_filename = datetime_str + "_"
    if userid:
        final_filename = final_filename + userid + "_"
    final_filename = Path(final_filename + Path(filename).name).with_suffix(".log")

    log_dir = get_root() / default_dir
    if not log_dir.is_dir():
        log_dir.mkdir(exist_ok=True)
    log_filename = log_dir / final_filename

    logging.basicConfig(
        filename=log_filename,
        level=level,  # Set the desired log level
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
