import audioop
import base64
from io import BytesIO
import json
import traceback
from fastapi.responses import PlainTextResponse
import numpy as np
from voxprobe.utils.audio_processing_utils import get_vad_pipeline
from .telephony_tester import TelephonyTester
from twilio.rest import Client
import os
from fastapi import FastAPI, Request, WebSocket, Query, WebSocketDisconnect
import uvicorn
import subprocess
import time
import requests
import threading
from twilio.twiml.voice_response import VoiceResponse, Connect
import soundfile as sf

class TwilioTester(TelephonyTester):
    def __init__(self, agent, dataset, twilio_account_sid=None, twilio_auth_token=None, twilio_incoming_number=None):
        super().__init__()
        print("Initializing TwilioTester...")
        self.agent = agent
        self.dataset = dataset
        self.app = FastAPI()
        self.ngrok_process = None
        self.ngrok_url = None
        self.twilio_client = None
        
        # Use provided values or fall back to environment variables
        self.twilio_account_sid = twilio_account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = twilio_auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_incoming_number = twilio_incoming_number or os.getenv("TWILIO_INCOMING_NUMBER")

    def configure(self):
        print("Configuring TwilioTester...")
        self.setup_fastapi()
        self.start_ngrok()
        self.setup_twilio()
        print("TwilioTester configuration complete.")

    def setup_fastapi(self):
        print("Setting up FastAPI...")
        @self.app.post("/twilio/callback")
        async def twilio_callback(request: Request):
            print("Twilio callback received")
            
            # Create a TwiML response
            response = VoiceResponse()
            
            # Add the WebSocket connection using the ngrok URL
            websocket_twilio_route = f"wss://{self.ngrok_url.split('//')[1]}/twilio/ws"
            connect = Connect()
            connect.stream(url=websocket_twilio_route)
            print(f"WebSocket connection done to {websocket_twilio_route}")
            response.append(connect)
            
            return PlainTextResponse(str(response), status_code=200, media_type='text/xml')
        

        @self.app.websocket("/twilio/ws")
        async def websocket_endpoint(websocket: WebSocket, user_agent: str = Query(None)):
            print("Connected to ws")
            await websocket.accept()
            agent_config, context_data = None, None
            buffer = []
            message_count = 0
            stream_sid = None
            speech_started = False
            final_audio = b''
            call_sid = None
            should_end_call = False
            
            chunk_files = sorted([f for f in os.listdir("left_channel_segments") if f.startswith('chunk_') and f.endswith('.wav')],
                         key=lambda x: int(x.split('_')[1].split('.')[0]))
            print(chunk_files)
            CURRENT_CHUNK = 0
            try:
                print(f"Connected to websocket")
                while True:
                    try:
                        message = await websocket.receive_text()
                        packet = json.loads(message)
                        if packet['event'] == 'start':
                            print(f"Started calling {packet}")
                            stream_sid = packet['start']['streamSid']
                            if call_sid is None and "callSid" in packet['start']:
                                print(f"Setting call_sid {packet['start']['callSid']}")
                                call_sid = packet['start']['callSid']

                        elif packet['event'] == 'media':
                            
                            if call_sid is None and "callSid" in packet:
                                print(f"Setting call_sid {packet['callSid']}")
                                call_sid = packet['callSid']
                            #print(f"Started getting response")
                            if 'chunk' in packet['media'] or ('track' in packet['media'] and packet['media']['track'] == 'inbound'):
                                media_data = packet['media']
                                media_audio = base64.b64decode(media_data['payload'])
                                media_ts = int(media_data["timestamp"])
                                last_media_received = media_ts
                                buffer.append(media_audio)
                                message_count += 1
                                if message_count == 50:
                                    print("message count higher than 50")
                                    # Concatenate the buffer and check if it contains any speech
                                    full_audio = b''.join(buffer) 
                                    buffer.clear()
                                    message_count = 0

                                    # Convert mulaw audio to PCM for processing
                                    audio_stream = audioop.ulaw2lin(full_audio, 2)
                                    final_audio += audio_stream
                                    #audio_stream = audioop.ratecv(audio_stream, 2, 1, 8000, 16000, None)[0]
                                    
                                    # # with open(f"op/trial_audio_{datetime.now()}.wav", 'wb') as f:
                                    # #     f.write(audio_stream)
                                    audio_stream = np.frombuffer(audio_stream, dtype=np.int16).reshape(-1, 1)
                                    wav_buffer = BytesIO()

                                    # # Write the linear PCM data to the buffer as a WAV file
                                    sf.write(wav_buffer, audio_stream, 8000, format='WAV')
                                    wav_buffer.seek(0)  # Rewind the buffer to the beginning so it can be read
                                    
                                    # Use VAD to detect if the audio contains speech  
                                    vad_pipeline = get_vad_pipeline()  
                                    vad_result = vad_pipeline(wav_buffer)
                                    total_speech_duration = vad_result.get_timeline().duration()
                                    
                                    if total_speech_duration > 0 and not speech_started:
                                        speech_started = True
                                        print(f"Assistant speech started")
                                    elif speech_started and total_speech_duration == 0:
                                        print("Detected empty noise in the buffer")
                                        if should_end_call:
                                            print("Got to end the call, creating task to get recording")
                                            # self.loop.create_task(process_followup_task(call_sid, stream_sid))
                                            await websocket.close()
                                            break
                                        # with wave.open(f"op/trial_audio_{datetime.now()}.wav", 'wb') as wav_file:
                                        #     wav_file.setnchannels(2)
                                        #     wav_file.setsampwidth(2)
                                        #     wav_file.setframerate(8000)
                                            
                                        #     # Convert the audio stream to the appropriate format
                                        #     #wav_data = struct.pack(f'{len(final_audio)//2}h', *struct.unpack(f'{len(final_audio)//2}h', final_audio))
                                        #     wav_file.writeframes(audio_stream) 
                                        #     final_audio = b''            
                                        
                                        current_chunk_name = chunk_files[CURRENT_CHUNK]
                                        file_path = os.path.join("left_channel_segments", current_chunk_name)    
                                        with open(file_path, 'rb') as f:
                                            audio = f.read()
                                        CURRENT_CHUNK +=1
                                        audio_data = audioop.lin2ulaw(audio, 2)
                                        base64_audio = base64.b64encode(audio_data).decode("utf-8")
                                        message = {
                                            'event': 'media',
                                            'streamSid': stream_sid, 
                                            'media': {
                                                'payload': base64_audio
                                            }
                                        }
                                        await websocket.send_text(json.dumps(message))
                                        speech_started = False
                                        if CURRENT_CHUNK == len(chunk_files)-1:
                                            print("We've reached the end")
                                            should_end_call = True
                                    elif speech_started:
                                        print("Detected speech in the buffer buit speech is alrerady going on")
                                    else:
                                        print("Just waiting for agent to speak")
                            else:
                                print("Not an inbound track")

                    except Exception as e:
                        traceback.print_exc()
                        print(f"Something wriong went here {e}")
                        await websocket.close()
                        break

            except WebSocketDisconnect:
                print("Websocket disconnected")
            except Exception as e:
                traceback.print_exc()
                print(f"error in executing {e}")

        print("FastAPI setup complete.")

    def start_ngrok(self):
        print("Starting ngrok...")
        self.ngrok_process = subprocess.Popen(["ngrok", "http", "8000"], stdout=subprocess.PIPE)
        time.sleep(2)  # Wait for ngrok to generate a public URL

        try:
            self.ngrok_url = requests.get("http://localhost:4040/api/tunnels").json()["tunnels"][0]["public_url"]
            print(f"ngrok tunnel established: {self.ngrok_url}")
        except requests.exceptions.ConnectionError:
            print("Failed to get ngrok tunnel. Make sure ngrok is running and the API is accessible.")
        print("ngrok started successfully.")

    def setup_twilio(self):
        print("Setting up Twilio...")
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_incoming_number]):
            raise ValueError("Twilio credentials or incoming number not provided")
        
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        voice_url = f"{self.ngrok_url}/twilio/callback"

        for num in self.twilio_client.incoming_phone_numbers.list():
            if num.phone_number == self.twilio_incoming_number:
                num.update(voice_url=voice_url)
                print(f"Updated Twilio number {self.twilio_incoming_number} with voice_url: {voice_url}")
                break
        else:
            print(f"Twilio number {self.twilio_incoming_number} not found")
        print("Twilio setup complete.")

    def run_test(self):
        print("Running test...")
        # TODO: Implement test logic
        super().run_test()
        print("Test completed.")

    def teardown(self):
        print("Tearing down...")
        if self.ngrok_process:
            self.ngrok_process.terminate()
        super().teardown()
        print("Teardown complete.")

    def start_server(self):
        print("Starting server...")
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

    def run(self):
        print("Starting TwilioTester run...")
        self.configure()
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        try:
            self.run_test()
        finally:
            self.teardown()
        print("TwilioTester run completed.")