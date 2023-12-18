
import argparse
from .construct_schedule import construct_schedule
from .make_events import make_events
from .make_journal_entries import make_journal_entries
from .make_schedule_files import make_schedule_files
from server.transfer import insert_profile_data
from utils.server import remove_profile
from utils.io import delete_directory_contents

def simulate_profile():

    # parse args
    argparser = argparse.ArgumentParser(description='Simulate a profile')
    argparser.add_argument('--profile', type=str, default='llm_v0', help='Profile to simulate')
    # argparser.add_argument('--make_events', action='store_true', help='Make events')
    argparser.add_argument('--entries', action='store_true', help='Make journal entries')
    argparser.add_argument('--reset', action='store_true', help='Reset profile')
    argparser.add_argument('--transfer', action='store_true', help='Transfer profile')
    args = argparser.parse_args()


    print()
    # reset profile if necessary
    if args.reset:
        remove_profile(args.profile)
        print("Profile removed from database\n")

    # first make schedule files
    simulated_events = construct_schedule(profile=args.profile)
    print("Schedule constructed\n")

    # make events
    make_events(simulated_events, profile=args.profile)
    print("Events created\n")

    # make journal entries
    if args.entries:
        make_schedule_files(profile=args.profile, overwrite=True)
        make_journal_entries(profile=args.profile)
        print("Journal entries created\n")

    if args.transfer:
        insert_profile_data(args.profile)
        print("Profile data transferred to database\n")

if __name__ == '__main__':
    simulate_profile()