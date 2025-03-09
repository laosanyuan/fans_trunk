from peewee import CharField, Model,  DateTimeField, BooleanField, IntegerField, ForeignKeyField, AutoField

from db.models.user import User
from db.models.fleet import Fleet


class Channel(Model):
    """频道信息

    Args:
        Model (_type_): _description_
    """
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    title = CharField(max_length=255)
    user = ForeignKeyField(User, backref='channels', on_delete='CASCADE')
    fleed = ForeignKeyField(Fleet, backref='channels')
    is_enable = BooleanField(default=False)
    is_access = BooleanField(default=False)
    score = IntegerField(default=0)
    add_time = DateTimeField()
    is_banned = BooleanField(default=False)

    class Meta:
        database = None
