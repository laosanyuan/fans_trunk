from datetime import datetime

from db.models.user import User
from db.models.channel import Channel
from models.channel_dto import ChannelDTO


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
    def get_channels(uid: int) -> list[Channel]:
        result = User.get(User.id == uid).channels
        return result

    @staticmethod
    def get_user_fleets(uid: int) -> list[ChannelDTO]:
        # 获取用户车队列表
        result = User.get_or_none(User.id == uid).channels

        list = []
        if result != None:
            for item in result:
                list.append(ChannelDTO.from_model(item))

        return list
