from db.models.fleet import Fleet


class FleetDTO:
    def __init__(self, id: int, name: str, min_score: int, max_score: int, member_count: int, channel_count: int):
        self.id = id
        self.name = name
        self.min_score = min_score
        self.max_score = max_score
        self.member_count = member_count
        self.channel_count = channel_count

    @classmethod
    def from_model(cls, fleet_model: Fleet):
        return cls(
            id=fleet_model.id,
            name=fleet_model.name,
            min_score=fleet_model.min_score,
            max_score=fleet_model.max_score,
            member_count=fleet_model.member_count,
            channel_count=fleet_model.channel_count
        )
