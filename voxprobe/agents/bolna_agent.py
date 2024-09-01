import functools
import os
import requests
from .agent import Agent

class BolnaAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__('bolna')  # Initialize the base class with the platform name
        self.api_key = kwargs.get('api_key', os.getenv('BOLNA_API_KEY'))  # Use api_key from kwargs if provided
        self.base_url = 'https://api.bolna.dev'
        self.agent_details = {}  # Dictionary to store details for multiple agents

    @functools.lru_cache(maxsize=1000)
    def _make_api_request(self, endpoint, method='GET', data=None):
        url = f'{self.base_url}/{endpoint}'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def pull(self, agent_id):
        """Pull the latest agent details from the Bolna API for a specific agent ID."""
        endpoint = f'agent/{agent_id}'
        self.agent_details[agent_id] = self._make_api_request(endpoint)  # Store details in the dictionary
        return self.agent_details[agent_id] is not None

    def evaluate(self):
        """Evaluate the agent's performance."""
        # This method would typically involve analyzing the agent's responses
        # and comparing them to expected outcomes. For now, we'll just return
        # a placeholder result.
        return {
            'accuracy': 0.85,
            'response_time': 1.2,
            'user_satisfaction': 0.9
        }

    def get_prompt(self, agent_id):
        """Retrieve the agent's prompt for a specific agent ID."""
        if agent_id not in self.agent_details:
            self.pull(agent_id)  # Ensure details are pulled for the specific agent ID
        
        agent_prompts = self.agent_details[agent_id].get("agent_prompts", {})
        if agent_prompts:
            return agent_prompts.get("task_1", {}).get('assistantDescription', [{}])[0].get('children', [{}])[0].get("text")
        return None

    def get_first_message(self, agent_id):
        """Retrieve the agent's welcome message for a specific agent ID."""
        if agent_id not in self.agent_details:
            self.pull(agent_id)  # Ensure details are pulled for the specific agent ID
        
        return self.agent_details[agent_id].get("agent_welcome_message")

    def get_executions(self):
        """Retrieve the agent's execution history."""
        endpoint = f'agent/{self.agent_id}/executions'
        executions = self._make_api_request(endpoint)
        return executions if executions else []
        return executions if executions else []

