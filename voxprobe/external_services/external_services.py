
class ExternalServices:
    def __init__(self):
        self.elevenlabs = ElevenLabsService()
        self.deepgram = DeepgramService()
        self.litellm = LiteLLMService()

    def generate_voice(self, text, voice_id):
        return self.elevenlabs.generate_voice(text, voice_id)

    def transcribe_audio(self, audio):
        return self.deepgram.transcribe_audio(audio)

    def generate_text(self, prompt, params):
        return self.litellm.generate_text(prompt, params)

