import sys
from pathlib import Path

p = Path(__file__).resolve()
while p.name != "src":
    p = p.parent
sys.path.append(str(p))

# get all the nids


def get_profile_dir(profile):
    return Path(root_path).parent / "data/sim/profiles" / profile
