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
