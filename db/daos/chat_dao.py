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
    def update_publish_message(channel_id: int, message_id: int) -> None:
        """更新发布消息
        """
        if ChatDao.is_exists(channel_id):
            ChatMessage.update(message_id=message_id, push_time=datetime.now(), is_newest=True)\
                .where(ChatMessage.channel_id == channel_id)\
                .execute()
        else:
            ChatMessage.create(channel_id=channel_id, message_id=message_id, push_time=datetime.now(), is_newest=True)

    @staticmethod
    def set_message_invalidate(channel_id: int):
        """设置频道消息过期
        """
        ChatMessage.update(is_newest=False)\
            .where(ChatMessage.channel_id == channel_id)\
            .execute()
