import openai
from utils.io import load_text_from_file
from utils.dates import convert_datetime, calculate_end_time, extract_date
import utils.keys as keys
from pathlib import Path
import json

# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo-1106" # this is faster!

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def make_entry_prompt(biography, information):
    prompt = "Please pretend that you are the person described in the following short biography:\n\n" + biography + \
    "\n\nNow, I will provide you with information regarding events that you experienced on a particular day:\n\n" + information + \
    "\n\nNow, please write a journal entry from the following perspective: " \
    "After you have wrapped up all of your activities for the day and are preparing to turn in, " \
    "describe your thoughts and emotions about the day. Be candid and concise. You do not need to" \
    "state the date at the beginning of your entry. You may begin writing now." 
    return prompt

def process_files(biography_file_path, information_file_paths, entry_dir):
    biography = load_text_from_file(biography_file_path)
    entries = []  # List to store all entries
    for file_path in information_file_paths:
        information = load_text_from_file(file_path)
        prompt = make_entry_prompt(biography, information)
        response = get_completion(prompt, MODEL)

        # set up date
        date = Path(file_path).stem
        start_time = "23:55:00"
        duration = {'minutes': 5}
        start_datetime = convert_datetime(date, start_time)
        end_datetime = calculate_end_time(start_datetime, duration)

        entry_data = {
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "entry": response,
            }            
        entries.append(entry_data)

    # Write all entries to a single file
    all_entries_path = entry_dir /  'journal_entries.json'
    with open(all_entries_path, 'w') as file:
        json.dump(entries, file, indent=4)

def get_file_paths(directory):
    file_paths = [filepath for filepath in Path(directory).glob('*.txt')]
    file_paths = sorted(file_paths, key=extract_date)
    return file_paths

def make_journal_entries(profile='llm_v0'):

    biography_file_path = 'prompts/bio.txt'

    # set up directories
    profile_dir = Path.cwd().parent /'data'/'sim' / 'profiles'/profile

    # List of information file paths
    information_file_folder = profile_dir / 'outputs' / 'intermediate' / 'temp_schedule_files'
    information_file_paths = get_file_paths(information_file_folder)
    # information_file_paths = information_file_paths[:] # for testing purposes

    # Create a directory for the journal entries
    entry_dir = profile_dir / 'outputs' / 'final'
    entry_dir.mkdir(parents=True, exist_ok=True)

    # Set up OpenAI API key
    openai.api_key = keys.OPENAI

    # Process each file
    process_files(biography_file_path, information_file_paths, entry_dir)


