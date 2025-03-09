from peewee import CharField, Model,  DateTimeField, ForeignKeyField,AutoField

from db.models.channel import Channel


class ChatMessage(Model):
    """消息数据

    Args:
        Model (_type_): _description_
    """
    id = AutoField(primary_key=True)
    chat_id = CharField(max_length=255)
    channel = ForeignKeyField(Channel, backref='messages', on_delete='CASCADE')
    push_time = DateTimeField()

    class Meta:
        database = None
