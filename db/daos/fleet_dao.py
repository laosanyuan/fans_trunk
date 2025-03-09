from db.models.fleet import Fleet
from models.fleet_dto import FleetDTO


class FleetDao:
    @staticmethod
    def update_fleet(id: int, name: str, min_score: int, max_score: int) -> None:
        # 更新车队数据
        is_exists = Fleet.select().where(Fleet.id == id).exists()
        if is_exists:
            Fleet.update(name=name, min_score=min_score, max_score=max_score)\
                .where(Fleet.id == id)\
                .execute()
        else:
            Fleet.create(id=id, name=name, min_score=min_score, max_score=max_score)

    @staticmethod
    def get_fleet(score: int) -> FleetDTO:
        # 根据评分获取车队
        result = Fleet.get(score >= Fleet.min_score and score < Fleet.max_score)
        return FleetDTO.from_model(result)

    @staticmethod
    def update_status(id: int, fans_count: int, channel_count: int) -> None:
        # 更新车队覆盖数据
        Fleet.update(all_fans_count=fans_count, all_channel_count=channel_count)\
            .where(Fleet.id == id)\
            .execute()