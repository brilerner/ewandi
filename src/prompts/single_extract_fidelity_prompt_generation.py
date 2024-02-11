def get_system(inputs_dict, current_date, current_time):
    inputs = "\n".join([f"- {k}: {v}" for k, v in inputs_dict.items()])

    prompt = f"""You are part of an application that allows a user to query their data. Your job is to simulate the user prompt and return it in the form of a JSON with a single key-value pair. The key should be "prompt" and the value should be the user prompt. Use only the information provided in the input to generate the prompt. The goal is to simulate a prompt that is realistic and natural for a person to ask about their life, which can take the form of a command or a question.

Guidelines:
The current day is {current_date}. The current time is {current_time}.
If no date or timing information, then no references to date or time should be made. E.g if only a variable is given, then no timing-related words such as "recently" should be used.

Here are specific guidelines for each input:
- variable:
    - contextualize as necessary, e.g. infer that "video games" semantically means "playing video games"
- people:
    - may use 1) common phrases such as "friends", or 2) refer to specific people
- date_range:
    - may use 1) common phrases such as "last month" or "yesterday", or 2) the format "YYYY-MM-DD--YYYY-MM-DD"
    - for a date_range of the form "YYYY-MM-DD--", assume that the end date is the current date
- time_range:
    - may use 1) common phrases such as "morning" or "night", or 2) the format "HH:MM--HH:MM"
    - if the end time is "00:00", assume that it is midnight of the next day
- days:
    - may use 1) common phrases such as "weekend" or "weekdays", or 2) the format ["Mon", "Tue"]


Examples:
    Command
        Input: 
        - variables: went to the movies
        - date_range: 2023-10-01--2023-10-10
        - time_range: 06:00-09:00
        Output: 
        {{'prompt': 'Please tell me how many times I went to the movies from 6-9am from October 1st to October 10th.'}}

    Question
        Input:
        - variables: hung out
        - date_range: "the last month"
        - days: "weekend"
        Output:
        {{'prompt': 'How often did I hang out on weekends over the last month?'}}

Here is the input:
{inputs}
Go!"""

    return prompt
