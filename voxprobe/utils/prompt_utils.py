from ..constants import CONVERSATION_GRAPH_SCHEMA

def get_agent_persona_prompt(agent_prompt):
    return f"""
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

def get_user_personas_prompt(role, goals_objectives, knowledge_skills):
    return f"""
    Task: Generate a comprehensive list of personas that an employee of {role} might interact with over the phone while performing their primary responsibilities.
    
    Given employee has the following traits:
    goals and objectives: {goals_objectives}
    knowledge and skills: {knowledge_skills}
    
    To approach this task, let's think through it step by step:

    1. Consider the main responsibilities of a {role}.
    2. Think about the types of people they might need to communicate with to fulfill these responsibilities.
    3. Consider different demographics, roles, and situations that might lead to interactions.
    4. For each persona, provide a brief explanation of why they might interact with the {role}.

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
    """


def get_user_scenarios_prompt(agent_persona, persona):
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
                "situation": "Brief name of the situation",
                "description": ""
            }},
            ...
        ]
        }}

        Generate as many relevant situations as possible, considering various combinations of persona traits. Be creative and thorough in your considerations.

        Begin your response now:
        """
        return prompt

def get_user_flows_prompt(agent_persona, persona, situation, conversation_graph, agent_instructions):
    prompt = f"""
    Task: Generate realistic conversation flows between an {agent_persona.role} and a {persona.persona} in the following situation:

    Situation: {situation.situation}

    Agent Role: {agent_persona.role}
    Agent Traits: {', '.join(agent_persona.personality_traits)}
    Agent Communication Style: {agent_persona.communication_style}
    Agent Instructions: {agent_instructions}

    Persona: {persona.persona}
    Persona Explanation: {persona.explanation}

    Potential Flows: {', '.join(situation.potential_flows)}

    Conversation Graph:
    States: {', '.join([state.name for state in conversation_graph.states])}
    Start State: {conversation_graph.start_state}
    End States: {', '.join(conversation_graph.end_states)}

    Generate conversation flows that reflect this situation, the characteristics of both the agent and the persona, and follow the given conversation graph. Consider both positive and negative flows.

    Please provide your response in the following format:

    {{
    "flows": [
        {{
            "conversation_flow": {{
                "states": ["state1", "state2", "state3", ...]
            }},
            "explanation": "Detailed explanation of this conversation flow"
        }},
        ...
    ]
    }}

    Generate multiple conversation flows based on the given situation, potential flows, and conversation graph. Include both successful and unsuccessful conversation paths.

    Begin your response now:
    """
    return prompt

def get_user_background_noises_prompt(role):
    return f"""
    Task: Generate a comprehensive list of potential background noises that might occur during a phone call with an {role}.

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
    """

def get_user_voices_prompt(role, traits):
    return f"""
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

def create_conversation_graph_prompt(agent_prompt, personas, scenarios):
    prompt = f"""
    You are an AI assistant tasked with creating a structured conversation graph based on a given scenario, personas, and potential situations. Your output must strictly adhere to the provided JSON schema.

    Scenario: {agent_prompt}

    Personas:
    {[f"- {persona.persona}: {persona.explanation}" for persona in personas.personas]}

    Potential Situations:
    {[f"- {situation.situation}: {', '.join(situation.potential_flows)}" for scenarios in scenarios for situation in scenarios.situations]}

    Instructions:
    1. Analyze the scenario, personas, and potential situations to identify key states in the conversation.
    2. Define transitions between these states, including any conditions for transitions based on different personas and situations.
    3. Determine the start state and possible end states.
    4. Think step by step and provide all possible ways the conversation can flow, both positive and negative, considering the various personas and situations.
    5. Structure your response according to the following JSON schema:

    {CONVERSATION_GRAPH_SCHEMA}

    Requirements:
    - Each state must have a unique id (e.g., "s1", "s2", etc.).
    - State names should be concise but descriptive.
    - Include relevant descriptions for states when applicable, mentioning specific personas or situations if relevant.
    - Ensure all transitions reference valid state ids.
    - The start_state must be one of the defined state ids.
    - All end_states must be valid state ids.
    - Provide a comprehensive graph that covers the entire conversation flow, including branches for different personas and situations.

    Your response should be a valid JSON object that can be directly parsed into the ConversationGraph structure. Do not include any explanations or additional text outside of the JSON object.

    Generate the conversation graph now:
    """
    return prompt

def create_persona_llm_prompt(agent_persona, persona, situation, flow):
    prompt = f"""
    You are an AI assistant tasked with simulating a conversation between an agent and a persona. The persona has specific traits and is in a particular situation. The conversation should follow a given flow of states. Your task is to generate the conversation turns, ensuring the conversation follows the flow and ends appropriately.

    Agent Persona:
    - Role: {agent_persona.role}
    - Personality Traits: {', '.join(agent_persona.personality_traits)}
    - Communication Style: {agent_persona.communication_style}
    - Knowledge/Skills: {', '.join(agent_persona.knowledge_skills)}
    - Goals/Objectives: {', '.join(agent_persona.goals_objectives)}

    Persona:
    - Name: {persona.persona}
    - Explanation: {persona.explanation}

    Situation:
    - Description: {situation.situation}
    - Potential Flows: {', '.join(situation.potential_flows)}

    Conversation Flow:
    - States: {', '.join(flow.conversation_flow.states)}

    Instructions:
    1. Start the conversation with the initial state.
    2. Follow the flow of states sequentially.
    3. Generate conversation turns for both the agent and the persona.
    4. Ensure the conversation ends when the flow reaches the final state.
    5. Indicate if the conversation should stop after the final state.

    Your response should be a valid JSON object that can be directly parsed into the PersonaLLMResponse structure. Do not include any explanations or additional text outside of the JSON object.

    Generate the conversation now:
    """
    return prompt