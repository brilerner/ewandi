# , default: null

# "label": "<label_name>", // string, required
# "start_time": "<start_time>", // string, format: "HH:MM", optional
# "end_time": "<end_time>", // string, format: "HH:MM", optional
# "people": [<people>, // list, optional
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")
current_time = datetime.now().strftime("%H:%M")

prompt = f"""The user will input a query or directive regarding one or more variables. Extract the following information as a JSON:
    {{
        "k": "<variable_keyphrase>", string, required
        "p": <associated_people>, // list, optional
        "dr": "<start_date>-<end_date>", // string, format: "YYYY-MM-DD:YYYY-MM-DD", optional
        "tr": "<start_time>-<end_time>", // string, format: ""HH:MM-HH:MM"", optional
        "ds": <days>, // list of strings, format: ["ddd",...], optional
    }}
The time may be inferred from phrases such as "morning" or "evening". The current date is {current_date}. The current time is {current_time}.
If a start/end date or time is not identified, it should be left blank, i.e. "dr": "-2021-09-30" or "tr": "-12:00".
For input such as "this month", "this week", "today", "tomorrow", "yesterday", the date should be inferred from the current date.
In the variable_keyphrase, including any words from the input that are important for context, such as "playing videogames" instead of simply "video games". Exclude words that relate to the variable operation such as "how often" or "frequency".
The days shoule be formatted as "Mon", "Tue" for specific days, "WD" for weekdays, "WE" for weekends. If no days are specified, it should not be included in the JSON.
Optional information should not be included if it is not present in the query. 
Here is an example:
Input: "How often did I eat pizza last month from 6-8am?"
Output: {{'k': 'eat pizza', 'dr': '2023-12-01:2023-12-31', 'tr': '06:00-08:00'}}
Go!
"""

# prompt = f"""The user will input a query or directive regarding one or more variables. Extract the following information:
#     {{
#         "k": "<variable_keyphrase>", string, required
#         "st": "<start_time>", // string, format: "HH:MM", optional
#         "et": "<end_time>", // string, format: "HH:MM", optional
#         "p": <associated_people>, // list, optional
#     }}
# Return a JSON containing the following information:
#     {{
#         "v": <variable_info> // list of dicts, required
#         "sd": "<start_date>", // string, format: "YYYY-MM-DD", optional
#         "ed": "<end_date>", // string, format: "YYYY-MM-DD", optional
#         "ds": <days>, // list of strings, format: ["ddd",...], optional
#     }}
# The time may be inferred from phrases such as "morning" or "evening". The current date is {current_date}. The current time is {current_time}.
# In the variable_keyphrase, including any words from the input that are important for context, such as "playing videogames" instead of simply "video games".
# Optional information should not be included if it is not present in the query.
# Go!
# """


# prompt = f"""The user will input a query or directive regarding one or more variables. For each variable present, extract the following information:
#     {{
#         "keyphrase": "<variable_keyphrase>", string, required
#         "start_time": "<start_time>", // string, format: "HH:MM", optional
#         "end_time": "<end_time>", // string, format: "HH:MM", optional
#         "people": <associated_people>, // list, optional
#     }}
# Return a JSON containing the following information:
#     {{
#         "variables": <variable_info> // list of dicts, required
#         "operations": <operations>, // list of dicts, required, default: null
#         "start_date": "<start_date>", // string, format: "YYYY-MM-DD", optional
#         "end_date": "<end_date>", // string, format: "YYYY-MM-DD", optional
#         "days": <days>, // list of strings, format: ["ddd",...], optional
#     }}
# Each dictionary in <operations> should have the following format:
#     {{
#         "type": "<operation_type>", // string, required
#         "variables": <variables>, // list of strings, required
#     }}
# The time may be inferred from phrases such as "morning" or "evening". The current date is {current_date}. The current time is {current_time}.
# Optional information should not be included if it is not present in the query.
# Go!
# """
