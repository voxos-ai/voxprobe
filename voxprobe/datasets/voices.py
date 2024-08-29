import json
from pydantic import BaseModel, Field
from typing import List, Dict
import random
from litellm import completion

class VoiceProfile(BaseModel):
    pitch: str = Field(..., description="Voice pitch (e.g., low, medium, high)")
    speed: str = Field(..., description="Speaking speed (e.g., slow, moderate, fast)")
    accent: str = Field(..., description="Accent or dialect")
    tone: str = Field(..., description="Overall tone of voice (e.g., warm, professional, energetic)")
    unique_characteristics: List[str] = Field(default_factory=list, description="Any unique voice characteristics")

class Voices(BaseModel):
    agent_voice: VoiceProfile = Field(..., description="Voice profile for the agent")
    persona_voices: Dict[str, VoiceProfile] = Field(..., description="Voice profiles for each persona")

    @classmethod
    def generate_voices(cls, agent_persona, personas):
        agent_voice = cls._generate_voice_profile(agent_persona.role, agent_persona.personality_traits)
        
        persona_voices = {}
        for persona in personas.personas:
            persona_voices[persona.persona] = cls._generate_voice_profile(persona.persona, [])

        return cls(agent_voice=agent_voice, persona_voices=persona_voices)

    @staticmethod
    def _generate_voice_profile(role, traits):
        prompt = f"""
        Generate a realistic voice profile for a {role} with the following traits: {', '.join(traits)}.
        
        The voice profile should include:
        1. Pitch (low, medium, or high)
        2. Speaking speed (slow, moderate, or fast)
        3. Accent or dialect
        4. Overall tone of voice
        5. Any unique voice characteristics (list up to 3)

        Provide your response in the following JSON format:

        {{
            "pitch": "low/medium/high",
            "speed": "slow/moderate/fast",
            "accent": "description of accent or dialect",
            "tone": "description of overall tone",
            "unique_characteristics": ["characteristic 1", "characteristic 2", "characteristic 3"]
        }}
        """

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with generating realistic voice profiles."},
            {"role": "user", "content": prompt}
        ]

        resp = completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=VoiceProfile
        )

        return VoiceProfile.parse_obj(json.loads(resp.choices[0].message.content))

    def get_voice_profile(self, speaker):
        if speaker == "Agent":
            return self.agent_voice
        else:
            return self.persona_voices.get(speaker, random.choice(list(self.persona_voices.values())))
