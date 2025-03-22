from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import inject

from services.wxpusher_service import WxPusherService
from services.fleet_manager import FleetManager
from services.telegram.bot_manager import BotManager
from db.daos.user_dao import UserDao
from db.daos.fleet_dao import FleetDao


class SchedulerManager:
    @inject.autoparams()
    def __init__(self, wx_pusher: WxPusherService, fleet_manager: FleetManager, bot_manager: BotManager):
        self._wx_pusher = wx_pusher
        self._fleet_manager = fleet_manager
        self._bot_manager = bot_manager
        self._preview_channel_count = 0
        self._preview_member_count = 0


        self._scheduler = AsyncIOScheduler()

        # 日报
        self._scheduler.add_job(self._post_daily_report,
                                CronTrigger(hour=21, timezone=timezone("Asia/Shanghai")))
        # 评级更新
        self._scheduler.add_job(self._update_score,
                                IntervalTrigger(hours=4),
                                max_instances=1)
        # 检查频道消息
        self._scheduler.add_job(self._check_channel_message,
                                IntervalTrigger(minutes=3),
                                max_instances=1)

    def start(self):
        """启动调度器"""
        self._preview_channel_count,self._preview_member_count = FleetDao.get_channel_summary()
        self._scheduler.start()

    def stop(self):
        """停止调度器"""
        if self._scheduler.running:
            self._scheduler.pause()

    def _post_daily_report(self):
        message = f'用户数量：{UserDao.get_user_count()}\n'

        channels, members = FleetDao.get_channel_summary()
        message += f'频道数量：{channels}\n成员数量：{members}\n'
        message += f'频道变化：{(channels - self._preview_channel_count):+}\n成员变化：{(members - self._preview_member_count):+}'

        self._wx_pusher.push(f'{self._bot_manager.get_bot_name()} - 互推车日报', message)

        self._preview_channel_count = channels
        self._preview_member_count = members


    async def _update_score(self):
        """更新频道数据
        """
        await self._bot_manager.user_service.update_all_user_data()
        self._fleet_manager.update_fleets_data()

    async def _check_channel_message(self):
        # 检查更新频道消息
        await self._bot_manager.chat_service.check_chat()
