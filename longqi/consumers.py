from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis


class Chatting(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'ygj'
        self.r = R()
        # 加入聊天室
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开聊天室
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 通过WebSocket，接收数据
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.r.insert(message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # 通过WebSocket发送
        await self.send(text_data=json.dumps({
            'message': message
        }))


class R:
    def __init__(self):
        self.r = redis.Redis(host='192.168.0.214',
                             port=6379,
                             db=0,
                             decode_responses=True)

    def insert(self, txt):
        return self.r.set('top_info', txt)

    def get(self):
        return self.r.get('top_info')

