from .telephony_tester import TelephonyTester
from twilio.rest import Client
import os
from fastapi import FastAPI, Request
import uvicorn
import subprocess
import time
import requests
import threading

class TwilioTester(TelephonyTester):
    def __init__(self, agent, dataset):
        super().__init__()
        self.agent = agent
        self.dataset = dataset
        self.app = FastAPI()
        self.ngrok_process = None
        self.ngrok_url = None
        self.twilio_client = None

    def configure(self):
        self.setup_fastapi()
        self.start_ngrok()
        self.setup_twilio()

    def setup_fastapi(self):
        @self.app.post("/twilio_callback")
        async def twilio_callback(request: Request):
            print("Twilio callback received")
            # TODO: Implement callback logic
            return {"message": "Callback received"}

    def start_ngrok(self):
        self.ngrok_process = subprocess.Popen(["ngrok", "http", "8000"], stdout=subprocess.PIPE)
        time.sleep(2)  # Wait for ngrok to generate a public URL

        try:
            self.ngrok_url = requests.get("http://localhost:4040/api/tunnels").json()["tunnels"][0]["public_url"]
            print(f"ngrok tunnel established: {self.ngrok_url}")
        except requests.exceptions.ConnectionError:
            print("Failed to get ngrok tunnel. Make sure ngrok is running and the API is accessible.")

    def setup_twilio(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_client = Client(account_sid, auth_token)
        
        incoming_number = os.getenv("TWILIO_INCOMING_NUMBER")
        voice_url = f"{self.ngrok_url}/twilio_callback"

        for num in self.twilio_client.incoming_phone_numbers.list():
            if num.phone_number == incoming_number:
                num.update(voice_url=voice_url)
                print(f"Updated Twilio number {incoming_number} with voice_url: {voice_url}")
                break
        else:
            print(f"Twilio number {incoming_number} not found")

    def run_test(self):
        # TODO: Implement test logic
        super().run_test()

    def teardown(self):
        if self.ngrok_process:
            self.ngrok_process.terminate()
        super().teardown()

    def start_server(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

    def run(self):
        self.configure()
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        try:
            self.run_test()
        finally:
            self.teardown()
