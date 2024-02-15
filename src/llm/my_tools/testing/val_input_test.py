import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))


from server.retrieve import get_data, get_elements, get_embeddings, get_events
from utils.dates import convert_time, keep_time, keep_date
from datetime import datetime

from llm.my_tools.validation import validate_input

events = get_events()

start_date = '2023-09-01'
end_date = '2023-09-01'
# end_date = '2023-12-31'
start_time = '12:00'
end_time = None
days = ['Fri']
v = 'talking on the phone'
people = ['Mom']


start_date = None
end_date = None
start_time = None
end_time = None
days = None
people = None


v = 'avocado'
people=['Mom']
start_date = '2023-09-01'
end_date = '2023-09-10'

def make_range(start, end):
    if not start and not end:
        return None
    if not start:
        start = ''
    if not end:
        end = ''
    return start + '--' + end
dr = make_range(start_date, end_date)
tr = make_range(start_time, end_time)
val_events = validate_input(v, people, dr, tr, days)