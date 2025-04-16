import requests
import json

with open('config.json') as f:
    config = json.load(f)

class SlackClient:
    def __init__(self,username):
        self.url = config['slack']['url']
        self.token = config['slack']['token']
        self.username = username

    def send_message(self, channel, message):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'channel': channel,
            'text': message,
        }
        if self.username:
            data['username'] = self.username
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()
