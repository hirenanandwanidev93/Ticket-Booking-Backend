from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json, time


class EventConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'event'
        if "CE_id=" in self.scope["query_string"].decode():
            self.room_group_name = self.scope["query_string"].decode().replace(
                "CE_id=", "")
        else:
            self.room_group_name = "All-FrontEnd-Users"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print("Accepted new socket connection below.")
        print(self.scope["query_string"].decode())
        self.accept()
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'heartbeat',
        #         'time': time.time()
        #     }
        # )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECED CODE: ", code)

    def receive(self, text_data=None, bytes_data=None):
        print(" MESSAGE RECEIVED")
        data = json.loads(text_data)
        print(data)
        # message = data

    def send_message_to_frontend(self, event):
        print("EVENT TRIGERED")
        print(self.room_group_name)
        # Receive message from room group
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def heartbeat(self, event):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'heartbeat',
                'time': time.time()
            }
        )
