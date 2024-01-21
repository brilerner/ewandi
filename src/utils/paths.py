import sys
from pathlib import Path

root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

# get all the nids

def get_profile_dir(profile):
    return Path(root_path).parent / "data/sim/profiles" / profile

