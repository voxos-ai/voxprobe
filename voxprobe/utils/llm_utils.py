from litellm import completion
from pydantic import BaseModel
import json


def generate(model: str, user_prompt: str, system_prompt: str = None, response_model: BaseModel = None, ):

    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    if response_model:
        response = completion(
            response_format=response_model,
            messages=messages,
            model=model
        )
        return response_model.parse_obj(json.loads(response.choices[0].message.content))
    else:
        response = completion(
            messages=messages,
            model=model
        )
        return response.choices[0].message.content