from peewee import Model,  DateTimeField, ForeignKeyField, AutoField, IntegerField

from db.models.channel import Channel


class ChatMessage(Model):
    """消息数据

    Args:
        Model (_type_): _description_
    """
    id = AutoField(primary_key=True)
    message_id = IntegerField()
    channel = ForeignKeyField(Channel, backref='messages', on_delete='CASCADE')
    push_time = DateTimeField()

    class Meta:
        database = None
