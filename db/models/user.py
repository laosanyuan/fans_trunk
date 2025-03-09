from peewee import CharField, Model,  DateTimeField, BooleanField, AutoField, IntegerField


class User(Model):
    """用户信息

    Args:
        Model (_type_): _description_
    """
    id = IntegerField(primary_key=True)
    user_name = CharField(max_length=255)
    full_name = CharField(max_length=255)
    add_time = DateTimeField()
    is_banned = BooleanField(default=False)

    class Meta:
        database = None
