import json
from pydantic import BaseModel, Field
from typing import List
from litellm import completion

class ConversationTurn(BaseModel):
    speaker: str = Field(..., description="The speaker of this turn (e.g., 'Agent' or 'Customer')")
    message: str = Field(..., description="The content of the speaker's message")

class Conversation(BaseModel):
    turns: List[ConversationTurn] = Field(..., description="List of conversation turns")

class Flows(BaseModel):
    conversations: List[Conversation] = Field(..., description="List of conversation flows")

    @classmethod
    def generate_flows(cls, agent_persona, persona, situation):
        prompt = f"""
        Task: Generate a realistic conversation flow between an {agent_persona.role} and a {persona.persona} in the following situation:

        Situation: {situation.situation}

        Agent Role: {agent_persona.role}
        Agent Traits: {', '.join(agent_persona.personality_traits)}
        Agent Communication Style: {agent_persona.communication_style}

        Persona: {persona.persona}
        Persona Explanation: {persona.explanation}

        Potential Flows: {', '.join(situation.potential_flows)}

        Generate a conversation that reflects this situation and the characteristics of both the agent and the persona. The conversation should have a natural flow and demonstrate how the interaction might realistically unfold.

        Please provide your response in the following format:

        {{
        "conversations": [
            {{
                "turns": [
                    {{
                        "speaker": "Agent or Customer",
                        "message": "The content of the message"
                    }},
                    ...
                ]
            }}
        ]
        }}

        Generate one or more conversation flows based on the given situation and potential flows.

        Begin your response now:
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with generating realistic conversation flows."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=cls
        )

        return cls.parse_obj(json.loads(resp.choices[0].message.content))
