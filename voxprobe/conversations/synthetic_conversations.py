from pydantic import BaseModel, Field
from typing import List
import random

class SyntheticTurn(BaseModel):
    speaker: str
    message: str
    background_noise: str = None
    voice_profile: dict = None

class SyntheticConversation(BaseModel):
    turns: List[SyntheticTurn] = Field(default_factory=list)
    persona: str
    situation: str

    def add_turn(self, speaker, message, background_noise=None, voice_profile=None):
        self.turns.append(SyntheticTurn(
            speaker=speaker, 
            message=message, 
            background_noise=background_noise,
            voice_profile=voice_profile
        ))

    @classmethod
    def from_flow(cls, flow, persona, situation, background_noises, voices):
        synthetic_conv = cls(persona=persona, situation=situation)
        for turn in flow.turns:
            noise = random.choice(background_noises) if background_noises else None
            voice_profile = voices.get_voice_profile(turn.speaker).dict()
            synthetic_conv.add_turn(turn.speaker, turn.message, noise, voice_profile)
        return synthetic_conv
