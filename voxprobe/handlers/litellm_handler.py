from litellm import completion
from voxprobe.utils.llm_utils import generate
from pydantic import BaseModel

class LiteLLMHandler:
    def __init__(self):
        # TODO: Initialize LiteLLM client
        pass

    def generate(self, prompt, params):
        model = params.get("model")
        system_prompt = params.get("system_prompt")
        response_model = params.get("response_model")

        return generate(model=model, user_prompt=prompt, system_prompt=system_prompt, response_model=response_model)