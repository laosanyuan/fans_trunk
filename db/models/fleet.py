from peewee import CharField, Model, IntegerField


class Fleet(Model):
    """车队信息

    Args:
        Model (_type_): _description_
    """
    id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    min_score = IntegerField(default=0)
    max_score = IntegerField(default=100)
    all_fans_count = IntegerField(default=0)
    all_channel_count = IntegerField(default=0)

    class Meta:
        database = None
