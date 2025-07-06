from db.daos.fleet_dao import FleetDao


class ChannelDataProvider:

    def get_all_summary(self) -> tuple[int, int]:
        """获取所有频道汇总
        """
        real_channels, real_memebers = FleetDao.get_channel_summary()

        return real_channels, real_memebers

    def get_fleet_summary(self, fleet_id: int) -> tuple[int, int]:
        """获取指定车队的汇总信息
        """
        fleet = FleetDao.get_fleet_by_id(fleet_id)
        return fleet.channel_count, fleet.member_count
