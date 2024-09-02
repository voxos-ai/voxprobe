import functools
import os
import requests
from .agent import Agent

class BolnaAgent(Agent):
    def __init__(self, agent_id, **kwargs):
        super().__init__('bolna')  # Initialize the base class with the platform name
        self.api_key = kwargs.get('api_key', os.getenv('BOLNA_API_KEY'))  # Use api_key from kwargs if provided
        self.base_url = 'https://api.bolna.dev'
        self.agent_id = agent_id
        self.agent_details = None

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
        self.agent_details = self._make_api_request(endpoint)  # Store details in the dictionary
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
        if not self.agent_details:
            self.pull()  # Ensure details are pulled for the specific agent ID
        
        agent_prompts = self.agent_details.get("agent_prompts", {})
        if agent_prompts:
            return agent_prompts.get("task_1", {}).get('assistantDescription', [{}])[0].get('children', [{}])[0].get("text")
        return None

    def get_first_message(self):
        """Retrieve the agent's welcome message."""
        if not self.agent_details:
            self.pull()  # Ensure details are pulled for the specific agent ID
        
        return self.agent_details.get("agent_welcome_message")

    def get_executions(self):
        """Retrieve the agent's execution history."""
        endpoint = f'agent/{self.agent_id}/executions'
        executions = self._make_api_request(endpoint)
        return executions if executions else []

    def make_call(self, recipient_phone_number, from_phone_number=None, user_data=None):
        """
        Make a call using the Bolna API.
        
        :param recipient_phone_number: The phone number to call
        :param from_phone_number: The phone number to call from
        :param user_data: Optional dictionary of user data to pass to the agent
        :return: The response from the API call
        """
        endpoint = 'call'
        print(f"Making call to {recipient_phone_number} with agent id {self.agent_id}")
        data = {
            "agent_id": self.agent_id,
            "recipient_phone_number": recipient_phone_number
        }
        if from_phone_number:
            data["from_phone_number"] = from_phone_number
        if user_data:
            data["user_data"] = user_data
        response = self._make_api_request(endpoint, method='POST', data=data)
        print(f"Response = {response} \nConversation id for the call {response['call_id']}") 
        return response['call_id']

    def get_call_status(self, execution_id):
        """
        Get the status of a specific call execution.

        :param execution_id: The ID of the call execution to check
        :return: A dictionary containing the call execution details, or None if the request fails
        """
        endpoint = f'agent/{self.agent_id}/execution/{execution_id}'
        return self._make_api_request(endpoint)

    def is_call_complete(self, execution_id):
        """
        Check if a call is complete.

        :param execution_id: The ID of the call execution to check
        :return: True if the call is complete, False if it's not, or None if the request fails
        """
        execution_details = self.get_call_status(execution_id)
        if execution_details is None:
            return None

        status = execution_details.get('status')
        return status not in ['in-progress', 'queued', 'ringing', 'initiated']