from collections import defaultdict
from voxprobe.utils.prompt_utils import create_persona_llm_prompt
from ..models import ConversationGraph, Flows, Persona, VoiceProfile, Voices
from ..models import AgentPersona, Personas, Scenarios, Situation, Flow, BackgroundNoise, Voices
from ..utils import get_agent_persona_prompt, get_user_personas_prompt, get_user_scenarios_prompt, get_user_flows_prompt, get_user_background_noises_prompt, get_user_voices_prompt, create_conversation_graph_prompt
from ..utils import generate


class Dataset:
    def __init__(self, agent_prompt, agent_persona_prompt=None, user_persona_prompt=None, user_scenario_prompt=None, user_flow_prompt=None, user_background_noises_prompt=None, user_voice_prompt=None, conversation_graph = None, model = "gpt-4o-2024-08-06"):
        self.agent_persona = None
        self.personas = None
        self.scenarios = None
        self.flows = None
        self.background_noises = None
        self.voices = None
        self.synthetic_conversations = []
        self.agent_persona_prompt = agent_persona_prompt
        self.user_persona_prompt = user_persona_prompt
        self.user_scenario_prompt = user_scenario_prompt
        self.user_flow_prompt = user_flow_prompt
        self.user_background_noises_prompt = user_background_noises_prompt
        self.user_voice_prompt = user_voice_prompt
        self.agent_prompt = agent_prompt
        self.model = model
        self.conversation_graph = conversation_graph
        self.persona_scenario_flow_map = {}  # Updated attribute to maintain relationships
    
    def generate_agent_persona(self):
        print("Generating agent persona...")
        if self.agent_persona_prompt is None:
            base_prompt = get_agent_persona_prompt(self.agent_prompt)

        system_prompt = "You are an AI assistant tasked with analyzing agent prompts for a voice assistant and extracting persona details."
        self.agent_persona: AgentPersona = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=AgentPersona)
        print("Agent persona generated successfully.")

    def generate_personas(self):
        print("Generating personas...")
        if self.user_persona_prompt is None:
            role, goals_objectives, knowledge_skills = self.agent_persona.role, self.agent_persona.goals_objectives, self.agent_persona.knowledge_skills
            base_prompt = get_user_personas_prompt(role, goals_objectives, knowledge_skills)

        system_prompt = "You are an AI assistant tasked with generating personas based on the agent persona."
        self.personas = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=Personas)
        print(f"Generated {len(self.personas.personas)} personas.")

    def generate_scenarios(self, num_rows = None):
        print("Generating scenarios...")
        if not self.personas:
            raise ValueError("Personas must be generated before scenarios.")

        if num_rows is None:
            num_rows = float('inf')
            
        self.scenarios = []
        for persona in self.personas.personas:
            print(f"Persona: {persona.persona}")
            base_prompt = get_user_scenarios_prompt(self.agent_persona, persona)
            print(f"Base prompt: {base_prompt}")
            system_prompt = "You are an AI assistant tasked with generating scenarios for the given persona."
            print(f"Generating scenarios for persona: {persona.persona}")
            scenarios = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=Scenarios)
            self.scenarios.append(scenarios)
            self.persona_scenario_flow_map[persona.persona] = {'persona': persona, 'scenarios': {'situations': []}}
            for situation in scenarios.situations:
                self.persona_scenario_flow_map[persona.persona]['scenarios']['situations'].append({'situation': situation, 'flows': []})
            if len(self.scenarios) >= num_rows:
                print(f"Generated {len(self.scenarios)} scenarios and hence breaking.")
                break
        print(f"Generated {len(self.scenarios)} scenarios.")

    def generate_flows(self):
        print("Generating flows...")
        if not self.scenarios:
            raise ValueError("Scenarios must be generated before flows.")

        self.flows = []
        for persona_name, data in self.persona_scenario_flow_map.items():
            persona = data['persona']
            for situation_data in data['scenarios']['situations']:
                scenario = situation_data['situation']
                base_prompt = get_user_flows_prompt(self.agent_persona, persona, scenario, self.conversation_graph, self.agent_prompt)
                system_prompt = "You are an AI assistant tasked with generating flows for the given persona and situation."
                flow = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=Flows)
                print(f"Flow for scenario {scenario.situation} is {flow}")
                situation_data['flows'].extend(flow.flows)
                self.flows.extend(flow if isinstance(flow, list) else [flow])
        print(f"Generated {len(self.flows)} flows.")

    #TODO: Change it enough to include persona details
    def generate_background_noises(self):
        print("Generating background noises...")
        if self.agent_persona is None:
            raise ValueError("Agent persona must be generated before background noises.")

        base_prompt = get_user_background_noises_prompt(self.agent_persona.role)
        system_prompt = "You are an AI assistant tasked with generating background noises for the agent persona."
        self.background_noises = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=BackgroundNoise)
        print(f"Generated {len(self.background_noises.noises)} background noises.")

    def generate_voices(self):
        # Commented out original code
        # if self.agent_persona is None or self.personas is None:
        #     raise ValueError("Agent persona and personas must be generated before voices.")

        # base_prompt = get_user_voices_prompt(self.agent_persona.role, self.agent_persona.personality_traits)
        # system_prompt = "You are an AI assistant tasked with generating voice profiles for the agent persona and personas."
        # self.voices = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=Voices)

        # Returning fake data for voices
        self.voices = Voices(
            agent_voice=VoiceProfile(
                pitch="medium",
                speed="moderate",
                accent="Neutral American",
                tone="Professional",
                unique_characteristics=["Clear enunciation", "Slight raspiness"]
            ),
            persona_voices={
                "Customer": VoiceProfile(
                    pitch="low",
                    speed="slow",
                    accent="Southern US",
                    tone="Friendly",
                    unique_characteristics=["Drawl", "Occasional chuckle"]
                ),
                "Manager": VoiceProfile(
                    pitch="high",
                    speed="fast",
                    accent="British RP",
                    tone="Authoritative",
                    unique_characteristics=["Crisp consonants", "Rising intonation"]
                )
            }
        )
        print("Voices generated successfully.")

    def generate_conversation_graph(self):
        print("Generating conversation graph...")
        base_prompt = create_conversation_graph_prompt(self.agent_prompt, self.personas, self.scenarios)
        system_prompt = "You are an AI assistant tasked with generating a conversation graph of all the states the conversation regarding following goals and instruction to an agent can go in."
        self.conversation_graph = generate(self.model, base_prompt, system_prompt=system_prompt, response_model=ConversationGraph)
        print("Conversation graph generated successfully.")

    def generate_persona_llm_prompts(self, num_rows = None):
        prompts = []
        self.persona_prompt_ds = defaultdict(dict)
        for persona_name, data in self.persona_scenario_flow_map.items():
            persona = data['persona']
            for situation_data in data['scenarios']['situations']:
                situation = situation_data['situation']
                self.persona_prompt_ds[persona_name][situation.situation] = {'potential_flows': situation.potential_flows}
                for flow in situation_data['flows']:
                    prompt = create_persona_llm_prompt(self.agent_persona, persona, situation, flow)
                    prompts.append(prompt)
                    
                    self.persona_prompt_ds[persona_name][situation.situation]["prompts"] = prompt
                    self.persona_prompt_ds[persona_name][situation.situation]["flow"] = flow
                    if num_rows is not None and len(prompts) >= num_rows:
                        break
        return prompts

    def generate_dataset(self, num_rows = None):

        print("Starting dataset generation...")
            
        # Generate agent persona
        print("Generating agent persona...")
        self.generate_agent_persona()
        print("Agent persona generated successfully.")

        # Generate personas
        print("Generating personas...")
        self.generate_personas()
        print(f"Generated {len(self.personas.personas)} personas.")

        # Generate voice profiles
        # print("Generating voice profiles...")
        # self.generate_voices()
        # print(f"Generated {len(self.voices.agent_voices)} agent voices and {len(self.voices.persona_voices)} persona voices.")

        # Generate scenarios and flows for each persona
        print("Generating scenarios and flows...")
        self.generate_scenarios(num_rows= num_rows)

        if self.conversation_graph is None:
            print("Starting to generate conversation graph...")
            self.generate_conversation_graph()

        self.generate_flows()
        print(f"Generated {len(self.scenarios)} scenarios and {len(self.flows)} flows.")

        # Generate background noises
        print("Generating background noises...")
        self.generate_background_noises()
        print(f"Generated {len(self.background_noises.noises)} background noises.")

        print(f"Generating persona llm prompts...")
        self.generate_persona_llm_prompts(num_rows= num_rows)
        print(f"Generated {len(self.persona_prompt_ds)} persona llm prompts.")
        
        print("Generating permutations...")
        self.permutations = []
        i = 0
        for persona_name, data in self.persona_scenario_flow_map.items():
            persona = data['persona']
            for scenario_data in data['scenarios']['situations']:
                scenario = scenario_data['situation']
                for flow in scenario_data['flows']:
                    noise = self.background_noises.noises[i]
                    i +=1
                    if i == len(self.background_noises.noises):
                        i =0
                    permutation = {
                        'persona': data['persona'],
                        'scenario': scenario,
                        'flow': flow,
                        'background_noise': noise,
                    }
                    self.permutations.append(permutation)
        
        print(f"Generated {len(self.permutations)} permutations.")
        print("Dataset generation completed successfully.")

        # # Generate synthetic conversations
        # for _ in range(num_conversations):
        #     persona = random.choice(self.personas.personas)
        #     scenario = random.choice([s for scenarios in self.scenarios for s in scenarios.situations])
        #     flow = random.choice(self.flows)
            
        #     synthetic_conv = SyntheticConversation.from_flow(
        #         flow, 
        #         persona.persona, 
        #         scenario.situation, 
        #         [noise.noise for noise in self.background_noises.noises],
        #         self.voices
        #     )
        #     self.synthetic_conversations.append(synthetic_conv)

    def save_dataset(self, path):
        import json
        import random
        with open(path, 'w') as f:
            json.dump({
                'agent_persona': self.agent_persona.dict(),
                'personas': self.personas.dict(),
                'background_noises': self.background_noises.dict(),
                'persona_prompt_ds': {
                    persona_name: {
                        situation: {
                            'prompt': data['prompts'],
                            'flow': data['flow'].dict(),
                            #'voice': random.choice(list(self.voices.persona_voices.values())).dict(),
                            'background_noise': random.choice(self.background_noises.noises).dict()
                        } for situation, data in situations.items()
                    } for persona_name, situations in self.persona_prompt_ds.items()
                }
            }, f, indent=2)

    def load_dataset(self, path):
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        self.agent_persona = AgentPersona.parse_obj(data['agent_persona'])
        self.personas = Personas.parse_obj(data['personas'])
        self.background_noises = BackgroundNoise.parse_obj(data['background_noises'])
        #self.voices = Voices.parse_obj(data['voices'])
        self.persona_scenario_flow_map = {
            persona_name: {
                'persona': Persona.parse_obj(map_data['persona']),
                'scenarios': {
                    'situations': [
                        {
                            'situation': Situation.parse_obj(situation_data['situation']),
                            'flows': [Flows.dict(flow) for flow in situation_data['flows']]
                        } for situation_data in map_data['scenarios']['situations']
                    ]
                }
            } for persona_name, map_data in data['persona_scenario_flow_map'].items()
        }
        self.permutations = [
            {
                'persona': Persona.parse_obj(perm['persona']),
                'scenario': Situation.parse_obj(perm['scenario']),
                'flow': Flows.parse_obj(perm['flow']),
                'background_noise': BackgroundNoise.parse_obj({'noises': [perm['background_noise']]})
            } for perm in data['permutations']
        ]