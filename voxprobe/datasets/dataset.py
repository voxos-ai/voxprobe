from .agent_persona import AgentPersona
from .personas import Personas
from .scenarios import Scenarios
from .flows import Flows
from .background_noise import BackgroundNoise
from conversations.synthetic_conversations import SyntheticConversation
from .voices import Voices
import random

class Dataset:
    def __init__(self, agent_prompt):
        self.agent_persona = None
        self.personas = None
        self.scenarios = None
        self.flows = None
        self.background_noises = None
        self.voices = None
        self.synthetic_conversations = []
        self.agent_prompt = agent_prompt

    def generate_dataset(self, num_conversations=100):
        # Generate agent persona
        self.agent_persona = AgentPersona.from_agent_prompt(self.agent_prompt)

        # Generate personas
        self.personas = Personas.generate_personas(self.agent_persona)

        # Generate background noises
        self.background_noises = BackgroundNoise.generate_background_noises(self.agent_persona)

        # Generate voice profiles
        self.voices = Voices.generate_voices(self.agent_persona, self.personas)

        # Generate scenarios and flows for each persona
        self.scenarios = []
        self.flows = []
        for persona in self.personas.personas:
            scenarios = Scenarios.generate_scenarios(self.agent_persona, persona)
            self.scenarios.append(scenarios)
            
            for situation in scenarios.situations:
                flows = Flows.generate_flows(self.agent_persona, persona, situation)
                self.flows.extend(flows.conversations)

        # Generate synthetic conversations
        for _ in range(num_conversations):
            persona = random.choice(self.personas.personas)
            scenario = random.choice([s for scenarios in self.scenarios for s in scenarios.situations])
            flow = random.choice(self.flows)
            
            synthetic_conv = SyntheticConversation.from_flow(
                flow, 
                persona.persona, 
                scenario.situation, 
                [noise.noise for noise in self.background_noises.noises],
                self.voices
            )
            self.synthetic_conversations.append(synthetic_conv)

    def save_dataset(self, path):
        import json
        with open(path, 'w') as f:
            json.dump({
                'agent_persona': self.agent_persona.dict(),
                'personas': self.personas.dict(),
                'scenarios': [s.dict() for s in self.scenarios],
                'background_noises': self.background_noises.dict(),
                'voices': self.voices.dict(),
                'synthetic_conversations': [conv.dict() for conv in self.synthetic_conversations]
            }, f, indent=2)

    def load_dataset(self, path):
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        self.agent_persona = AgentPersona.parse_obj(data['agent_persona'])
        self.personas = Personas.parse_obj(data['personas'])
        self.scenarios = [Scenarios.parse_obj(s) for s in data['scenarios']]
        self.background_noises = BackgroundNoise.parse_obj(data['background_noises'])
        self.voices = Voices.parse_obj(data['voices'])
        self.synthetic_conversations = [SyntheticConversation.parse_obj(conv) for conv in data['synthetic_conversations']]
