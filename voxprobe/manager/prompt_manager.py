import yaml
from typing import Dict

class PromptManager:
    def __init__(self, prompt_file: str = None):
        self.prompts: Dict[str, str] = {}
        if prompt_file:
            self.load_prompts(prompt_file)

    def load_prompts(self, prompt_file: str):
        with open(prompt_file, 'r') as file:
            self.prompts = yaml.safe_load(file)

    def get_prompt(self, prompt_name: str) -> str:
        return self.prompts.get(prompt_name, "")

    def set_prompt(self, prompt_name: str, prompt: str):
        self.prompts[prompt_name] = prompt

    def save_prompts(self, prompt_file: str):
        with open(prompt_file, 'w') as file:
            yaml.dump(self.prompts, file)
