from datetime import datetime

from peewee import fn

from db.models.channel import Channel
from db.models.fleet import Fleet
from models.channel_dto import ChannelDTO
from models.fleet_dto import FleetDTO


class ChannelDao:
    # 添加用户
    @staticmethod
    def add_channel(uid: int, channel_id: int, name: str, title: str, fleet_id: int, has_permission: bool, score: int, member_count: int) -> None:
        is_exists = Channel.select().where(Channel.id == channel_id).exists()
        if not is_exists:
            Channel.create(
                id=channel_id,
                name=name,
                title=title,
                user_id=uid,
                fleet_id=fleet_id,
                is_access=has_permission,
                score=score,
                add_time=datetime.now(),
                member_count=member_count)

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
    def get_message_channels(channel_id: int, count: int = 15) -> list[ChannelDTO]:
        """获取推广频道数据列表
        """
        target_channel: Channel = Channel.get(Channel.id == channel_id)
        channels = (Fleet.get(Fleet.id == target_channel.fleet_id)
                    .channels
                    .where(Channel.id != channel_id)
                    .order_by(fn.Random())  # 使用数据库随机排序
                    .limit(count))

        return [ChannelDTO.from_model(channel) for channel in channels]

    @staticmethod
    def update_member_count(channel_id: int, count: int, fleet_id: int) -> None:
        """更新频道成员数量
        """
        Channel.update(member_count=count, fleet_id=fleet_id)\
            .where(Channel.id == channel_id)\
            .execute()

    @staticmethod
    def get_fleet_chanels(fleet_id: int, count: int = 30) -> list[ChannelDTO]:
        """获取车队下的频道列表
        """
        channels = (Channel.select()
                    .where(
            (Channel.fleet_id == fleet_id) &
            (Channel.is_access == True) &
            (Channel.is_banned == False) &
            (Channel.is_enable == True)
        )
            .order_by(Channel.member_count.desc())  # 按成员数量降序排序
            .limit(count))

        return [ChannelDTO.from_model(channel) for channel in channels]

    @staticmethod
    def get_channels(count: int = 50) -> list[ChannelDTO]:
        """获取成员数量多的频道列表降序返回
        """
        channels = Channel.select().order_by(Channel.member_count.desc()).limit(count)

        return [ChannelDTO.from_model(item) for item in channels]

    @staticmethod
    def get_channel(id: int) -> ChannelDTO:
        """获取频道数据
        """
        return ChannelDTO.from_model(Channel.get(Channel.id == id))

    @staticmethod
    def get_channel_fleet(id: int) -> FleetDTO:
        """获取频道所在车队
        """
        result = Channel.get(Channel.id == id).fleet
        return FleetDTO.from_model(result)

    @staticmethod
    def update_score(channel_id: int, score: int) -> None:
        """更新评分
        """
        if ChannelDao.is_exists(channel_id):
            Channel.update(score=score).where(Channel.id == channel_id).execute()
