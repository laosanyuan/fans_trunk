import json


class FleetConfig:
    def __init__(self, user_name: str, min_score: float, max_score: float):
        self.user_name = user_name
        self.min_score = min_score
        self.max_score = max_score


class FleetService:
    def __init__(self, fleet_config: str) -> None:
        self.config_path = fleet_config
        self.datas = self._load_datas()

    def get_fleets(self) -> list[FleetConfig]:
        result = []
        for item in self.datas:
            tmp = FleetConfig(
                item['name'], item['min_score'], item['max_score'])
            result.append(tmp)
        return result

    def _load_datas(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
