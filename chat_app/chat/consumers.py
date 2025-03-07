# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatSession, Message
from django.utils.timezone import now

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle receiving messages from WebSocket"""
        data = json.loads(text_data)
        sender = self.scope["user"]
        content = data["message"]

        if sender.is_authenticated:
            # Save message in the database
            chat_session = await self.get_chat_session()
            message = await self.create_message(chat_session, sender, content)

            # Broadcast message to all users in the chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "sender": sender.username,
                    "content": message.content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )

    async def chat_message(self, event):
        """Send messages to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def get_chat_session(self):
        return await ChatSession.objects.aget(id=self.chat_id)

    async def create_message(self, chat_session, sender, content):
        return await Message.objects.acreate(chat=chat_session, sender=sender, content=content, timestamp=now())
