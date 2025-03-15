from datetime import datetime
import random

from db.models.channel import Channel
from db.models.fleet import Fleet
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

    @staticmethod
    def get_message_channels(channel_id, count: int = 15) -> list[ChannelDTO]:
        """获取推广频道数据列表
        """
        target_channel: Channel = Channel.get(Channel.id == channel_id)
        channels = Fleet.get(Fleet.id == target_channel.fleet_id).channels

        results = []
        for channel in channels:
            if channel.id == channel_id:
                continue
            results.append(ChannelDTO.from_model(channel))
        random.shuffle(results)

        return results
