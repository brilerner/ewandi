from server.query import get_schema

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

system = f"""You are Cerebra, a helpful assistant that pulls a user's personal data to help them know themselves better. You answer the user's question concisely and helpfully.
You always provide the stored name of the accessed data so the user can understand the process better.
Begin!"""

opener = """What would you like to know about yourself?"""

questions = [

    # "What is your name?",
    "How many times does the Basketball Game occur?"

]

schema = f"""The mapping between the dataset variable names and the categories they belong to:
{SCHEMA}
"""