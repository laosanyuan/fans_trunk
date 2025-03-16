from datetime import datetime

from db.models.channel import Channel


class ChannelDTO:
    def __init__(
        self,
        id: int,
        name: str,
        title: str,
        user_id: int,
        fleet_id: int,
        is_enable: bool,
        is_access: bool,
        score: int,
        add_time: datetime,
        is_banned: bool,
        member_count: int
    ):
        self.id = id
        self.name = name
        self.title = title
        self.user_id = user_id
        self.fleet_id = fleet_id
        self.is_enable = is_enable
        self.is_access = is_access
        self.score = score
        self.add_time = add_time
        self.is_banned = is_banned
        self.member_count = member_count

    @classmethod
    def from_model(cls, channel_model: Channel):
        """
        从 Channel 模型实例化 ChannelDTO。
        """
        return cls(
            id=channel_model.id,
            name=channel_model.name,
            title=channel_model.title,
            user_id=channel_model.user_id,
            fleet_id=channel_model.fleet_id,
            is_enable=channel_model.is_enable,
            is_access=channel_model.is_access,
            score=channel_model.score,
            add_time=channel_model.add_time,
            is_banned=channel_model.is_banned,
            member_count=channel_model.member_count
        )


class ChannelPage:
    def __init__(self, channels: list[ChannelDTO], page: int, page_size: int, total: int) -> None:
        self.channels = channels
        self.page = page
        self.page_size = page_size
        self.total = total

        self.is_first = page == 0
        self.is_last = (page+1)*page_size >= total
