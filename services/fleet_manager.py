import json

from db.daos.fleet_dao import FleetDao


class FleetManager:
    def __init__(self, fleet_config: str) -> None:
        self.config_path = fleet_config

    def init(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            datas = json.load(f)
        for item in datas:
            FleetDao.update_fleet(item['id'], item['name'], item['min_score'], item['max_score'])

    def update_fleets() -> None:
        pass
