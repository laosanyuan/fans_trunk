import os
import random
import json
from datetime import datetime

from db.daos.fleet_dao import FleetDao
from models.channel_dto import ChannelDTO

class FleetService:
    def __init__(self, fake_users_path:str = None) -> None:
        self._fake_users_path = fake_users_path
        self._fake_users = []
        if fake_users_path != None and os.path.exists(fake_users_path):
            self._fake_users = self._load_fake_users()

    def get_all_summary(self) -> tuple[int,int]:
        """获取所有频道汇总
        """
        real_channels,real_memebers = FleetDao.get_channel_summary()

        fake_channels = len(self._fake_users)
        fake_members = 0
        for item in self._fake_users:
            fake_members += item.member_count

        return real_channels + fake_channels,real_memebers+fake_members
    
    def get_fleet_summary(self,fleet_id:int) -> tuple[int,int]:
        """获取指定车队的汇总信息
        """
        fleet = FleetDao.get_fleet_by_id(fleet_id)

        fake_channels = 0
        fake_members = 0
        for item in self._fake_users:
            if item.member_count >= fleet.min_score and item.member_count<fleet.max_score:
                fake_channels += 1
                fake_members += item.member_count

        return fleet.channel_count + fake_channels, fleet.member_count + fake_members
    
    def get_fake_users(self,min_score:int,max_score:int,count:int) -> list[ChannelDTO]:
        """获取随机假用户
        """
        filtered_channels = [ch for ch in self._fake_users if ch.score >= min_score and ch.score < max_score]
        if len(filtered_channels) > count:
            result = random.sample(filtered_channels, count)
        else:
            result = filtered_channels
        return result


    def _load_fake_users(self) -> list[ChannelDTO]:
        """从配置文件加载广告数据"""
        try:
            with open(self._fake_users_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    tmp = ChannelDTO(-1,item['name'],item['title'],-1,-1,True,True,item['score'],datetime.now(),False,item['member_count'])
                    self._fake_users.append(tmp)
        except Exception as e:
            print(f"加载广告配置失败: {str(e)}")
            self._ads = []


        