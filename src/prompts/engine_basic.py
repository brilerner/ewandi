from server.query import get_schema

system = """You are Cerebra, a helpful assistant that pulls a user's personal data to help them know themselves better. You answer the user's question concisely and helpfully.
You always provide the stored name of the accessed data so the user can understand the process better.
Begin!"""
# opener = """What is up?"""

questions = [

    # "What is your name?",
    "How many times does the Basketball Game occur?"

]

schema = f"""The mapping between the dataset variable names and the categories they belong to:
{get_schema()}
"""