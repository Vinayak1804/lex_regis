import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Conversation, Message, ConversationStatus, MessageStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        is_participant, is_active = await self.check_conversation_access(self.conversation_id, self.user)
        if not is_participant or not is_active:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Broadcast online presence
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_presence',
                'user_id': self.user.id,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Broadcast offline presence
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_presence',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'send_message':
            content = data.get('content', '')
            if content.strip():
                msg = await self.save_message(self.conversation_id, self.user, content)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': msg.id,
                        'content': content,
                        'sender_id': self.user.id,
                        'sender_name': self.user.get_full_name(),
                        'created_at': msg.created_at.isoformat(),
                        'status': msg.status
                    }
                )
        elif action == 'typing_start':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': self.user.id,
                    'is_typing': True
                }
            )
        elif action == 'typing_stop':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': self.user.id,
                    'is_typing': False
                }
            )
        elif action == 'read_messages':
            message_ids = data.get('message_ids', [])
            if message_ids:
                await self.mark_messages_read(message_ids, self.user)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_read',
                        'message_ids': message_ids,
                        'reader_id': self.user.id
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': {
                'id': event['message_id'],
                'content': event['content'],
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
                'created_at': event['created_at'],
                'status': event['status']
            }
        }))

    async def typing_status(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            }))

    async def user_presence(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'presence',
                'user_id': event['user_id'],
                'status': event['status']
            }))
            
    async def messages_read(self, event):
        if event['reader_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'read_receipt',
                'message_ids': event['message_ids'],
                'reader_id': event['reader_id']
            }))

    @database_sync_to_async
    def check_conversation_access(self, conversation_id, user):
        try:
            conv = Conversation.objects.get(id=conversation_id)
            is_participant = conv.participants.filter(id=user.id).exists()
            is_active = conv.status in [ConversationStatus.ACTIVE, ConversationStatus.CLOSED]
            return is_participant, is_active
        except Conversation.DoesNotExist:
            return False, False

    @database_sync_to_async
    def save_message(self, conversation_id, user, content):
        conv = Conversation.objects.get(id=conversation_id)
        conv.last_message_at = timezone.now()
        conv.save(update_fields=['last_message_at'])
        return Message.objects.create(
            conversation=conv, 
            sender=user, 
            content=content,
            status=MessageStatus.SENT
        )
        
    @database_sync_to_async
    def mark_messages_read(self, message_ids, user):
        Message.objects.filter(
            id__in=message_ids, 
            conversation__participants=user
        ).exclude(sender=user).update(
            is_read=True, 
            read_at=timezone.now(),
            status=MessageStatus.READ
        )
