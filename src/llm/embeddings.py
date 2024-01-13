import scipy

from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

from utils.hardcoded import DEFAULT_EMBEDDING_MODEL



@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def request_embedding(text, model=DEFAULT_EMBEDDING_MODEL):
    """
    Input can be a single string or a list of strings
    """
    client = OpenAI()

    if isinstance(text, str):
            text = [text]

    response = client.embeddings.create(input = text, model=model)

    embeddings = [embedding.embedding for embedding in response.data]

    if len(embeddings) == 1:
        return embeddings[0]
    else:
        return embeddings
    

def get_distance(x,y, method='cosine'):

    if method == 'cosine':
        return scipy.spatial.distance.cosine(x,y)
    else:
        raise NotImplementedError('Only cosine distance is implemented')