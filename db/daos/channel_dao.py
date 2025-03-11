from datetime import datetime

from db.models.channel import Channel


class ChannelDao:
    # 添加用户
    @staticmethod
    def add_channel(uid: int, channel_id: int, name: str, title: str, fleet_id: int) -> None:
        is_exists = Channel.select().where(Channel.id == channel_id).exists()
        if not is_exists:
            Channel.create(id=channel_id, name=name, title=title, user_id=uid, fleet_id=fleet_id, add_time=datetime.now())

    @staticmethod
    def is_exists(channel_id) -> bool:
        return Channel.select().where(Channel.id == channel_id).exists()

    @staticmethod
    def remove_channel(channel_id: int):
        Channel.delete().where(Channel.id == channel_id).execute()
