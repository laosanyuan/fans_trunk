from datetime import datetime

from db.models.chat_message import ChatMessage
from models.chat_message_dto import ChatMessageDTO


class ChatDao:
    @staticmethod
    def is_exists(channel_id: int) -> bool:
        is_exists = ChatMessage.select().where(ChatMessage.channel_id == channel_id).exists()
        return is_exists

    @staticmethod
    def get_chat_message(channel_id: int) -> ChatMessageDTO:
        result = ChatMessage.get(ChatMessage.channel_id == channel_id)
        return ChatMessageDTO.from_model(result)

    @staticmethod
    def update_message(channel_id: int, meessage_id: int) -> None:
        if ChatDao.is_exists(channel_id):
            ChatMessage.update(meessage_id=meessage_id, push_time=datetime.now())\
                .where(ChatMessage.channel_id == channel_id)\
                .execute()
        else:
            ChatMessage.create(channel_id=channel_id, message_id=meessage_id, push_time=datetime.now())

    @staticmethod
    def get_message_id(channel_id: int) -> int:
        result = ChatMessage.get(ChatMessage.channel_id == channel_id)
        return result.message_id
