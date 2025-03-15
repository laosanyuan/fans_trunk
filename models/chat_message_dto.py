from datetime import datetime

from db.models.chat_message import ChatMessage


class ChatMessageDTO:
    def __init__(self, id: int, channel_id: int, push_time: datetime, is_newest: bool):
        self.message_id = id
        self.channel_id = channel_id
        self.push_time = push_time
        self.is_newest = is_newest

    @classmethod
    def from_model(cls, message_model: ChatMessage):
        return cls(
            id=message_model.message_id,
            channel_id=message_model.channel_id,
            push_time=message_model.push_time,
            is_newest=message_model.is_newest
        )
