import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

# get all the nids


def get_profile_dir(profile):
    return Path(root_path).parent / "data/sim/profiles" / profile
