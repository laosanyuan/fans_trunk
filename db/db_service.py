from db.db_connection import DatabaseConnection
from db.models.user import User
from db.models.channel import Channel
from db.models.chat_message import ChatMessage
from db.models.fleet import Fleet


class DbService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db_connection = DatabaseConnection(self.db_path)

    def init_db(self):
        # 初始化数据库连接
        self.db_connection.connect()

        # 设置数据库到模型
        User._meta.database = self.db_connection.db
        Channel._meta.database = self.db_connection.db
        ChatMessage._meta.database = self.db_connection.db
        Fleet._meta.database = self.db_connection.db

        # 创建表
        self.db_connection.create_tables([User, Channel, ChatMessage, Fleet])

    def close_db(self):
        self.db_connection.close()
