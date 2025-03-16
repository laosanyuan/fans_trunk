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
    def get_fleet_by_score(score: int) -> FleetDTO:
        # 根据评分获取车队
        result = Fleet.get(score >= Fleet.min_score and score < Fleet.max_score)
        return FleetDTO.from_model(result)

    @staticmethod
    def get_fleet_by_id(id: int) -> FleetDTO:
        result = Fleet.get(Fleet.id == id)
        return FleetDTO.from_model(result)

    @staticmethod
    def get_all_fleets() -> list[FleetDTO]:
        """获取所有车队信息"""
        return [FleetDTO.from_model(fleet) for fleet in Fleet.select()]

    @staticmethod
    def update_status(id: int, fans_count: int, channel_count: int) -> None:
        # 更新车队覆盖数据
        Fleet.update(all_fans_count=fans_count, all_channel_count=channel_count)\
            .where(Fleet.id == id)\
            .execute()

    @staticmethod
    def update_fleets_data() -> None:
        """更新频道实时数据
        """
        fleets = Fleet.select()
        for fleet in fleets:
            channel_count = len(fleet.channels)
            member_count = 0
            for tmp_channel in fleet.channels:
                member_count += tmp_channel.member_count
            Fleet.update(member_count=member_count, channel_count=channel_count)\
                .where(Fleet.id == fleet.id)\
                .execute()

    @staticmethod
    def get_channel_summary() -> tuple[int, int]:
        """获取频道数据汇总

        Returns:
            tuple[int, int]: 频道数量，成员数量
        """
        fleets = Fleet.select()
        channel_count = 0
        member_count = 0
        for fleet in fleets:
            channel_count += fleet.channel_count
            member_count += fleet.member_count
        return channel_count, member_count
