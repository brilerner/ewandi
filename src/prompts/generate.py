


system = """You are assisting me in the development of a new AI system. 
I am creating an application that can track a person's life and allow them to ask questions about their life using natural language. Assume that there is an existing database containing the names of events and related information. When a user interacts with my app, I will extract the key words/phrases from their query and check to see if the referenced variables currently exist in the database. I will ask you to perform a task that is related to this process.
"""



def groups(keystrings :list, descriptions=None):
    
    if descriptions:

        if len(keystrings) != len(descriptions):
            raise ValueError('keystrings and descriptions must be the same length')
        
        row_strings = []
        for keystring, description in zip(keystrings, descriptions):
            if description:
                row_strings.append(f'{keystring} : {description}')
            else:
                row_strings.append(f'{keystring}')
        input_string = '\n'.join(row_strings)
    else:
        input_string = '\n'.join(keystrings)

    prompt = f"""I am going to give you an input set of words/phrases, for which I would like you to generate a a set of group names that sufficiently capture the relationships between different members of the input set, where a group is a word/phrase that can be used to describe all members of the group.    
Any words/phrases in parentheses are there to add useful context. If a colon is present, the text after the colon provides further description.
Please return the group names as a JSON, i.e. {{'groups': ['group1', 'group2', 'group3', '...']}}. 
For example:
- if the input set contains 'basketball game' and 'basketball practice', 'basketball activities' would be a good group name.
- if the input set contains 'basketball game' and 'soccer game', 'sports' would be a good group name.
- if the input set contains 'reading' and 'watching TV', 'leisure activities' would be a good group name.
Here is the input set, where each row denotes a separate word/phrase:
{input_string}

Go!
"""

    return prompt

def classify_name(name, group, description=None):

    input_string = f"""Here is the name: {name}\nHere is the group: {group}"""
    if description:
        input_string += f"\nHere is the description: {description}"
    
    prompt = f"""I am going to give you a name and a group. Each is a string. I would like you to determine whether the name is a member of the group, where a group is a word/phrase that can be used to describe all members of the group Please return a JSON in the form of  {{'is_in_group': bool}}, where bool is a boolean value of True or False.
an input set of words/phrases, for which I would like you to generate a a set of group names that sufficiently capture the relationships between different members of the input set.     
Any words/phrases in parentheses are there to add useful context. The description, if present, is there to provide further information about the name.
{input_string}
Go!
"""
    return prompt

def nonexisting(names, n=5):

    input_string = '\n'.join(names)
    prompt = f"""I am going to give you a list of words/phrases which are related to a person's life.
Any words/phrases in parentheses provide useful context for the meaning of the rest of that particular string.
Please generate {n} new words/phrases that do not appear in the input list and are semantically different, but are realistic for the person's life given the input. 
The generated items should be phrased in a natural way, i.e. they should not have parentheses or formal punctuation even if members of the input list do.
Please return the new words/phrases as a JSON formatted as {{'items': ['item1', 'item2', 'item3', ...]}}.
Here are the input words/phrases:
{input_string}
Go!
"""
    return prompt

def variations(keystring, description=None, n=5):

    input_string = f"""Here is the input: {keystring}"""
    if description:
        input_string += f"\nHere is the description: {description}"

    prompt = f"""I am going to give you a word/phrase. I would like you to generate {n} variations of the word/phrase that are semantically similar to the input but are phrased differently.
Any words/phrases in parentheses in the input provide useful context for the meaning of the rest of that particular string.
The generated items should be phrased in a natural way, i.e. they should not have parentheses or formal punctuation even if members of the input list do.
The description, if present, is there to provide further context to aid in generating the variations.
Please return the new words/phrases as a JSON formatted as {{'variations': ['item1', 'item2', 'item3', ...]}}.
{input_string}
Go!
"""
    return prompt