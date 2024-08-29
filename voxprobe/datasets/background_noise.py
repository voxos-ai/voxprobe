import json
from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class Noise(BaseModel):
    noise: str = Field(..., description="Name or brief description of the noise")
    explanation: str = Field(..., description="Explanation of why this noise might occur")

class BackgroundNoise(BaseModel):
    noises: List[Noise] = Field(..., description="List of potential background noises")

    @classmethod
    def generate_background_noises(cls, agent_persona):
        prompt = f"""
        Task: Generate a comprehensive list of potential background noises that might occur during a phone call with an {agent_persona.role}.

        Let's approach this task step by step:

        1. Consider the likely environment(s) where this agent might be making or receiving phone calls.
        2. Think about the time of day and how it might affect background noises.
        3. Reflect on potential activities that might be happening in the background.
        4. Consider both common and uncommon sounds that could occur in these settings.

        For each background noise, provide:
        - A name or brief description of the noise
        - An explanation of why this noise might occur given the agent's role and their likely environment

        Please provide your response in the following format:

        {{
        "noises": [
            {{
                "noise": "Name or description of the noise",
                "explanation": "Explanation of why this noise might occur"
            }},
            ...
        ]
        }}

        Generate as many relevant background noises as possible, considering various scenarios and environments. Be creative and thorough in your considerations.

        Begin your response now:
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with generating background noises for various scenarios."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=cls
        )

        return cls.parse_obj(json.loads(resp.choices[0].message.content))
