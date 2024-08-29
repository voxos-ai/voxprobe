import os
import requests
from .agent import Agent

class BolnaAgent(Agent):
    def __init__(self, config):
        super().__init__('bolna', config)
        self.api_key = os.getenv('BOLNA_API_KEY')
        self.base_url = 'https://api.bolna.dev'
        self.agent_id = config.get('agent_id')

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

    def pull(self):
        """Pull the latest agent details from the Bolna API."""
        endpoint = f'agent/{self.agent_id}'
        self.agent_details = self._make_api_request(endpoint)
        return self.agent_details is not None

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

    def get_prompt(self):
        """Retrieve the agent's prompt."""
        if not hasattr(self, 'agent_details'):
            self.pull()
        
        agent_prompts = self.agent_details.get("agent_prompts", {})
        if agent_prompts:
            return agent_prompts.get("task_1", {}).get('assistantDescription', [{}])[0].get('children', [{}])[0].get("text")
        return None

    def get_first_message(self):
        """Retrieve the agent's welcome message."""
        if not hasattr(self, 'agent_details'):
            self.pull()
        
        return self.agent_details.get("agent_welcome_message")

    def get_executions(self):
        """Retrieve the agent's execution history."""
        endpoint = f'agent/{self.agent_id}/executions'
        executions = self._make_api_request(endpoint)
        return executions if executions else []

