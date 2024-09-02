from deepgram import DeepgramClient, PrerecordedOptions
import os

class DeepgramHandler:
    def __init__(self, api_key = None):
        if api_key is None:
            api_key = os.getenv("DEEPGRAM_API_KEY")
        print(f"Using Deepgram API key: {api_key}")
        self.dg_client = DeepgramClient(api_key)

    def transcribe_audio(self, audio, sample_rate, encoding="linear16", channels=1, language = "en-US"):
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            sample_rate=sample_rate,
            encoding=encoding,
            language=language,
            channels=channels
        )

        payload = {"buffer": audio}
        response = self.dg_client.listen.rest.v("1").transcribe_file(payload, options)
        print(f"Got Deepgram transcript {response}")
        return response

    def format_transcript(self, data, diarization):
        words = data['results']['channels'][0]['alternatives'][0]['words']
        current_speaker_index = 0
        current_speaker = diarization[current_speaker_index][2]
        transcript = []

        for word in words:
            word_start = word['start']
            word_end = word['end']
            
            while current_speaker_index < len(diarization) and word_start > diarization[current_speaker_index][1]:
                current_speaker_index += 1
                if current_speaker_index < len(diarization):
                    current_speaker = diarization[current_speaker_index][2]
            
            if current_speaker_index < len(diarization):
                if not transcript or transcript[-1]['speaker'] != current_speaker:
                    transcript.append({
                        'speaker': current_speaker, 
                        'words': [], 
                        'start': word_start, 
                        'end': word_end
                    })
                transcript[-1]['words'].append(word['punctuated_word'])
                transcript[-1]['end'] = word_end

        human_readable_transcript = []
        for entry in transcript:
            speaker = entry['speaker'].replace('_', ' ')
            words = ' '.join(entry['words'])
            start_time = entry['start']
            end_time = entry['end']
            human_readable_transcript.append(f"{speaker} ({start_time:.2f} - {end_time:.2f}): {words}")

        print('\n'.join(human_readable_transcript))
        return '\n'.join(human_readable_transcript)

