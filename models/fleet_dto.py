from db.models.fleet import Fleet


class FleetDTO:
    def __init__(self, id: int, name: str, min_score: int, max_score: int, all_fans_count: int, all_channel_count: int):
        self.id = id
        self.name = name
        self.min_score = min_score
        self.max_score = max_score
        self.all_fans_count = all_fans_count
        self.all_channel_count = all_channel_count

    @classmethod
    def from_model(cls, fleet_model: Fleet):
        return cls(
            id=fleet_model.id,
            name=fleet_model.name,
            min_score=fleet_model.min_score,
            max_score=fleet_model.max_score,
            all_fans_count=fleet_model.all_fans_count,
            all_channel_count=fleet_model.all_channel_count
        )
