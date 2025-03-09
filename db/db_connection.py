from peewee import SqliteDatabase


class DatabaseConnection:
    def __init__(self, db_path):
        self.db = SqliteDatabase(db_path)

    def connect(self):
        """连接数据库"""
        self.db.connect()

    def close(self):
        """关闭数据库连接"""
        if not self.db.is_closed():
            self.db.close()

    def create_tables(self, models):
        """创建所有模型对应的表"""
        with self.db.atomic():
            self.db.create_tables(models)
