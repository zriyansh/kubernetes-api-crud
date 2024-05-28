import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DeploymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']


        await self.channel_layer.group_send(
            'deployment_group',
            {
                'type': 'deployment_message',
                'message': message
            }
        )

    async def deployment_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
