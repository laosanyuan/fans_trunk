from datetime import datetime

from db.models.user import User
from db.models.channel import Channel


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
