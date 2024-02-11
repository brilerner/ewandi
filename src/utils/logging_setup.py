import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

from utils.general import get_root

import logging


def set_test(file):
    print("file:", file)
    print("__name__:", __name__)
    print("__package__:", __package__)
    print("__file__:", __file__)


def setup_logging(filename, userid=None, level=logging.INFO, default_dir="logs"):
    """
    Put the datetime in the log filename.
    """
    from datetime import datetime

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
