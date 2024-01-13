from server.query import get_schema

"""
- ask llm to offer suggestions to correct input?
"""


# this is to deal with a bug that occurs if I can't connect to the database
try:
    SCHEMA = get_schema()
except:
    SCHEMA = {}
# system = """You are Cerebra, a helpful assistant that pulls a user's personal data to help them know themselves better. You answer the user's question concisely and helpfully.
# You always provide the stored name of the accessed data so the user can understand the process better.
# Begin!"""


# schema = f"""The mapping between the dataset variable names and the categories they belong to:
# {get_schema()}
# """
# system = f"""You are Cerebra, a helpful assistant that pulls a user's personal data to help them know themselves better. You answer the user's question concisely and helpfully.
# The mapping between the dataset variable names and the categories they belong to:
# {get_schema()}. This can be used to determine the
# You always provide the stored name of the accessed data so the user can understand the process better.
# Begin!"""

system = """You are Cerebra, a helpful assistant that pulls a user's personal data to help them know themselves better. You answer the user's question concisely and helpfully.
You always provide the stored name of the accessed data so the user can understand the process better.
Begin!"""

openers = [
    """What would you like to know about yourself?""",
    """What can I help you with?""",
    """What would you like to know?"""
]
# def get_opener():
#     import random
#     openers = [
#         """What would you like to know about yourself?""",
#         """What can I help you with?""",
#         """What would you like to know?"""
#     ]
#     return random.choice(openers)

questions = [
    # "What is your name?",
    "How many times does the Basketball Game occur?"
]

schema = f"""The mapping between the dataset variable names and the categories they belong to:
{SCHEMA}
"""
