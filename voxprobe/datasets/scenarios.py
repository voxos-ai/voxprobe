import json
from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class Situation(BaseModel):
    situation: str = Field(..., description="Brief description of the situation")
    potential_flows: List[str] = Field(..., description="Potential conversation flows or decision points")

class Scenarios(BaseModel):
    situations: List[Situation] = Field(..., description="List of possible situations")

    @classmethod
    def generate_scenarios(cls, agent_persona, persona):
        prompt = f"""
        Task: Generate a comprehensive list of situations that could occur during a phone call for a job profile of {agent_persona.role}, considering the given persona.

        Agent Role: {agent_persona.role}
        Persona: {persona.persona}
        Persona Explanation: {persona.explanation}

        Let's approach this task step by step:

        1. Consider the main goals and potential obstacles in a {agent_persona.role} conversation.
        2. Think about how the persona's characteristics might influence the conversation flow.
        3. Consider common and uncommon scenarios that might arise during the conversation.

        For each situation, provide:
        - A brief description of the situation
        - Potential conversation flows or decision points

        Please provide your response in the following format:

        {{
        "situations": [
            {{
                "situation": "Brief description of the situation",
                "potential_flows": ["Flow 1", "Flow 2", ...]
            }},
            ...
        ]
        }}

        Generate as many relevant situations as possible, considering various combinations of persona traits. Be creative and thorough in your considerations.

        Begin your response now:
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with generating scenarios for various job profiles and personas."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=cls
        )

        return cls.parse_obj(json.loads(resp.choices[0].message.content))
