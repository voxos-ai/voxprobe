import json
from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class AgentPersona(BaseModel):
    role: str = Field(..., description="Agent's role or job title")
    personality_traits: List[str] = Field(..., description="Key personality traits of the agent")
    communication_style: str = Field(..., description="Agent's communication style")
    knowledge_skills: List[str] = Field(..., description="Specific knowledge or skills mentioned")
    goals_objectives: List[str] = Field(..., description="Goals or objectives of the agent")

    @classmethod
    def from_agent_prompt(cls, agent_prompt):
        prompt = f"""
        Analyze the following agent prompt and extract key details about the agent's persona:

        {agent_prompt}

        Please provide a structured response with the following information:
        1. Agent's role or job title
        2. Key personality traits (as a list)
        3. Communication style
        4. Any specific knowledge or skills mentioned (as a list)
        5. Goals or objectives of the agent (as a list)

        Format your response as a JSON object that matches the structure of the AgentPersona class.
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with analyzing agent prompts and extracting persona details."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=cls
        )

        return cls.parse_obj(json.loads(resp.choices[0].message.content))