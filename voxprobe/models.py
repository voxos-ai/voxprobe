from pydantic import BaseModel, Field 
from typing import List, Dict, Optional


class State(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    
class Transition(BaseModel):
    from_state: str
    to_state: str
    condition: Optional[str] = None

class ConversationGraph(BaseModel):
    states: List[State] = Field(default_factory=list)
    transitions: List[Transition] = Field(default_factory=list)
    start_state: str
    end_states: List[str] = Field(default_factory=list)

class ConversationFlow(BaseModel):
    states: List[str]

class AgentPersona(BaseModel):
    role: str = Field(..., description="Agent's role or job title")
    personality_traits: List[str] = Field(..., description="Key personality traits of the agent")
    communication_style: str = Field(..., description="Agent's communication style")
    knowledge_skills: List[str] = Field(..., description="Specific knowledge or skills mentioned")
    goals_objectives: List[str] = Field(..., description="Goals or objectives of the agent")

class ConversationTurn(BaseModel):
    speaker: str = Field(..., description="The speaker of this turn (e.g., 'Agent' or 'Customer')")
    message: str = Field(..., description="The content of the speaker's message")

class Conversation(BaseModel):
    turns: List[ConversationTurn] = Field(..., description="List of conversation turns")

class Flow(BaseModel):
    conversation_flow: ConversationFlow = Field(..., description="List of states conversation can flow to")
    explanation: str = Field(..., description="explaination of the conversation flow")

class Flows(BaseModel):
    flows: List[Flow] = Field(..., description="List of flows")

class Persona(BaseModel):
    persona: str = Field(..., description="The name or description of the persona")
    explanation: str = Field(..., description="Explanation of why this persona might interact with the job profile")

class Personas(BaseModel):
    personas: List[Persona] = Field(..., description="List of personas and their explanations")

class Noise(BaseModel):
    noise: str = Field(..., description="Name or brief description of the noise")
    explanation: str = Field(..., description="Explanation of why this noise might occur")

class BackgroundNoise(BaseModel):
    noises: List[Noise] = Field(..., description="List of potential background noises")

class Situation(BaseModel):
    situation: str = Field(..., description="Brief description of the situation")
    potential_flows: List[str] = Field(..., description="Potential conversation flows or decision points")

class Scenarios(BaseModel):
    situations: List[Situation] = Field(..., description="List of possible situations")

class VoiceProfile(BaseModel):
    pitch: str = Field(..., description="Voice pitch (e.g., low, medium, high)")
    speed: str = Field(..., description="Speaking speed (e.g., slow, moderate, fast)")
    accent: str = Field(..., description="Accent or dialect")
    tone: str = Field(..., description="Overall tone of voice (e.g., warm, professional, energetic)")
    unique_characteristics: List[str] = Field(default_factory=list, description="Any unique voice characteristics")

class Voices(BaseModel):
    agent_voice: VoiceProfile = Field(..., description="Voice profile for the agent")
    persona_voices: Dict[str, VoiceProfile] = Field(..., description="Voice profiles for each persona")


class PersonaLLMResponse(BaseModel):
    message: str = Field(..., description="The message to be sent to the agent")
    should_stop: bool = Field(..., description="Whether the conversation should stop")

class SituationDetail(BaseModel):
    prompt: str
    flow: Flow
    background_noise: Noise


class PersonaDataset(BaseModel):
    agent_persona: AgentPersona
    personas: Dict[str, List[Persona]]
    background_noises: Dict[str, List[Noise]]
    persona_prompt_ds: Dict[str, Dict[str, SituationDetail]]
