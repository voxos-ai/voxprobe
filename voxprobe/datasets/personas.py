import json
from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class Persona(BaseModel):
    persona: str = Field(..., description="The name or description of the persona")
    explanation: str = Field(..., description="Explanation of why this persona might interact with the job profile")

class Personas(BaseModel):
    personas: List[Persona] = Field(..., description="List of personas and their explanations")

    @classmethod
    def generate_personas(cls, agent_persona):
        prompt = f"""
        Task: Generate a comprehensive list of personas that a employee of {agent_persona.role} might interact with over the phone while performing their primary responsibilities.
        
        Given employee has the following traits:
        goals and objectives {agent_persona.goals_objectives}
        knowledge and skills {agent_persona.knowledge_skills}
        
        To approach this task, let's think through it step by step:

        1. Consider the main responsibilities of a {agent_persona.role}.
        2. Think about the types of people they might need to communicate with to fulfill these responsibilities.
        3. Consider different demographics, roles, and situations that might lead to interactions.
        4. For each persona, provide a brief explanation of why they might interact with the {agent_persona.role}.

        Please provide your response in the following format for each persona:

        {{
        "personas": [
            {{
                "persona": "Persona name or description",
                "explanation": "Explanation of why they might interact"
            }},
            ...
        ]
        }}

        Generate as many relevant personas as possible, drawing from your knowledge of various industries, roles, and human interactions. Be creative and thorough in your considerations.

        Begin your response now:
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with generating personas for various job profiles."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=cls
        )

        return cls.parse_obj(json.loads(resp.choices[0].message.content))
