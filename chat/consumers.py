import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Fetch the real user instance from self.scope['user']
        self.user = await database_sync_to_async(self.get_user)()

        if self.user.is_anonymous:
            # If the user is not authenticated, reject the connection
            print("Anonymous user detected, closing connection")
            await self.close()
        else:
            print(f"User in WebSocket connection: {self.user.username}")
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            print(f'chat_{self.room_name}')
            # Get or create a room object in the database asynchronously
            self.room, created = await database_sync_to_async(ChatRoom.objects.get_or_create)(
                name=self.room_group_name
            )

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group on disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle received messages
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save the message in the database asynchronously
        await database_sync_to_async(Message.objects.create)(
            room=self.room,
            user=self.user,  # Use the actual user instance
            content=message
        )

        # Broadcast the message to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username  # Send the user's username
            }
        )

    async def chat_message(self, event):
        # Receive message from room group
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    def get_user(self):
        """
        Helper method to return the real User instance from self.scope['user'].
        This ensures we are working with a proper User model, not a LazyObject.
        """
        if self.scope['user'].is_authenticated:
            return User.objects.get(pk=self.scope['user'].pk)
        return self.scope['user']  # Return AnonymousUser if not authenticated
