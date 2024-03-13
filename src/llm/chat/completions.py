import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) 
from openai import OpenAI
# GPT_MODEL = "gpt-3.5-turbo-1106"
GPT_MODEL = "gpt-4-1106-preview"
JSON_MODEL = "gpt-4-1106-preview"

#### simple

helicone_info = {
    "api_key": "sk-345rsyy-cxiemia-ve5mdoy-j7p2k7i",
    "base_url": "https://oai.hconeai.com/v1",
    "default_headers": {
        "Helicone-Auth": f"Bearer sk-345rsyy-cxiemia-ve5mdoy-j7p2k7i",
    },
}


def json_request_prompt_only(
    prompt, model=JSON_MODEL, role="user", load=True, **completions_kwargs
):
    # from helicone.openai_async import openai
    # client = OpenAI(**helicone_info)

    messages = [{"role": role, "content": prompt}]
    return json_request(messages, model=model, load=load, **completions_kwargs)
    # return json.loads(content)



@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def json_request(messages, model=JSON_MODEL, load=True, **completions_kwargs):
    import json

    from openai import OpenAI

    client = OpenAI()
    # messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        **completions_kwargs,
    )
    content = response.choices[0].message.content
    if load:
        return json.loads(content)
    else:
        return content


def get_completion(prompt, model=GPT_MODEL, response_format=None):
    client = OpenAI()
    messages = [{"role": "user", "content": prompt}]
    print(response_format)
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0, response_format=response_format
    )
    return response.choices[0].message.content


