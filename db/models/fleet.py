from peewee import CharField, Model, AutoField, IntegerField


class Fleet(Model):
    """车队信息

    Args:
        Model (_type_): _description_
    """
    id = AutoField(primary_key=True)
    name = CharField(max_length=255)
    min_score = IntegerField(default=0)
    max_score = IntegerField(default=100)
    all_fans_count = IntegerField()
    all_channel_count = IntegerField()

    class Meta:
        database = None
