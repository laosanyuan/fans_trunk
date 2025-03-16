from datetime import datetime

from db.models.user import User
from models.channel_dto import ChannelDTO, ChannelPage


class UserDao:
    # 添加用户
    @staticmethod
    def add_user(uid: int, user_name: str, full_name: str) -> None:
        is_exists = User.select().where(User.id == uid).exists()
        if not is_exists:
            User.create(id=uid, user_name=user_name, full_name=full_name, add_time=datetime.now())

    # 封禁用户
    @staticmethod
    def ban_user(uid: int) -> None:
        User.update(is_banned=True)\
            .where(User.id == uid)\
            .execute()

    @staticmethod
    def get_user_channels(uid: int, page: int, page_size: int = 5) -> ChannelPage:
        # 获取用户频道列表

        user = User.get_or_none(User.id == uid)
        if not user:
            return ChannelPage([], page, page_size, total=0)

        total = user.channels.count()
        # 计算偏移量
        offset = page * page_size
        channels = user.channels.limit(page_size).offset(offset)
        channel_list = [ChannelDTO.from_model(channel) for channel in channels]

        return ChannelPage(channel_list, page, page_size, total)
