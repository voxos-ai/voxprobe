
class Conversation:
    def __init__(self, id, agent, user, situation, background_noise, user_voice):
        self.id = id
        self.agent = agent
        self.user = user
        self.situation = situation
        self.background_noise = background_noise
        self.user_voice = user_voice
        self.flow = []
        self.transcript = []

    def add_turn(self, speaker, text):
        self.transcript.append({'speaker': speaker, 'text': text})

