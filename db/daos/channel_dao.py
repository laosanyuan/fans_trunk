from datetime import datetime

from db.models.channel import Channel
from models.channel_dto import ChannelDTO


class ChannelDao:
    # 添加用户
    @staticmethod
    def add_channel(uid: int, channel_id: int, name: str, title: str, fleet_id: int, has_permission: bool) -> None:
        is_exists = Channel.select().where(Channel.id == channel_id).exists()
        if not is_exists:
            Channel.create(id=channel_id, name=name, title=title, user_id=uid, fleet_id=fleet_id, is_access=has_permission, add_time=datetime.now())

    @staticmethod
    def is_exists(channel_id) -> bool:
        return Channel.select().where(Channel.id == channel_id).exists()

    @staticmethod
    def remove_channel(channel_id: int):
        Channel.delete().where(Channel.id == channel_id).execute()

    @staticmethod
    def update_permission(channel_id: int, has_permission: bool):
        Channel.update(is_access=has_permission).where(Channel.id == channel_id).execute()

    @staticmethod
    def get_all_validate_channels() -> list[ChannelDTO]:
        tmps = Channel.select().where(Channel.is_access == True and Channel.is_banned == False and Channel.is_enable == True)
        results = []
        for item in tmps:
            results.append(ChannelDTO.from_model(item))

        return results
