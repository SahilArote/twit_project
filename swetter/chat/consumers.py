# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from twit.models import twit
from .models import Message
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1 = self.scope['user'].username 
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([user1, user2]))}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']  
        post_id = text_data_json.get('post_id')
        receiver = await self.get_receiver_user() 

        await self.save_message(sender, receiver, message, post_id)
        
        payload ={
                'type': 'chat_message',
                'sender': sender.username,
                'receiver': receiver.username,
                'message': message
            }
        if post_id:
            post = await self.get_post(post_id)
            payload['post'] = {
                'id': post.id,
                'text': post.text,
                'photo': post.photo.url if post.photo else None,
            }

        await self.channel_layer.group_send(self.room_group_name, payload)



    async def chat_message(self, event):
        response = {
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message': event['message'],
        }

        if 'post' in event:
            response['post'] = event['post']

        await self.send(text_data=json.dumps(response))


    @sync_to_async
    def save_message(self, sender, receiver, message , post_id=None):
        post = twit.objects.get(id=post_id) if post_id else None
        Message.objects.create(sender=sender, receiver=receiver, content=message, post=post)

    @sync_to_async
    def get_receiver_user(self):
        return User.objects.get(username=self.room_name)
        
    @sync_to_async
    def get_post(self, post_id):
        return twit.objects.get(id=post_id)


