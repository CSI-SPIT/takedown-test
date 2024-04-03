import os
from dotenv import load_dotenv
from locust import HttpUser, task, between
import socketio


dotenv_path = os.path.join(os.getcwd(), '..', '.env')
load_dotenv(dotenv_path)

SOCKET_URI = os.environ.get("SOCKET_URI")
TEAM_ID = os.environ.get("TEAM_ID")
LOGIN_CODE = os.environ.get("LOGIN_CODE")

sio = socketio.Client()

@sio.event
def connect():
    print("Socket.IO connected")

@sio.event
def pong(data):
    print("Received pong")

class PlayerSim(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        response = self.client.post("/team/login", json={"team_id": TEAM_ID, "login_code": LOGIN_CODE})
        self.token = response.json()["token"]
        print("Authenticated. Token obtained:", self.token)

    @task
    def open_socket_io_connection(self):
        if not sio.connected:
            sio.connect(SOCKET_URI)

        sio.emit("tping")
        print("Sent ping event with token")

    def on_stop(self):
        # Disconnect from Socket.IO when the test is stopped
        if sio.connected:
            sio.disconnect()
            print("Disconnected from Socket.IO")
