from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import inject

from services.wxpusher_service import WxPusherService
from services.fleet_manager import FleetManager
from services.telegram.bot_manager import BotManager


class SchedulerManager:
    @inject.autoparams()
    def __init__(self, wx_pusher: WxPusherService, fleet_manager: FleetManager, bot_manager:BotManager):
        self._wx_pusher = wx_pusher
        self._fleet_manager = fleet_manager
        self._bot_manager = bot_manager

        self._scheduler = AsyncIOScheduler()

        # 日报
        self._scheduler.add_job(self._post_daily_report,
                                CronTrigger(hour=22, timezone=timezone("Asia/Shanghai")))
        # 评级更新
        self._scheduler.add_job(self._update_score,
                                IntervalTrigger(hours=4),
                                max_instances=1)
        # 检查频道消息
        self._scheduler.add_job(self._check_channel_message,
                                IntervalTrigger(seconds=1),
                                max_instances=1)

    def start(self):
        """启动调度器"""
        self._scheduler.start()

    def stop(self):
        """停止调度器"""
        if self._scheduler.running:
            self._scheduler.pause()

    def _post_daily_report(self):
        pass

    async def _update_score(self):
        await self._bot_manager.user_service.update_all_user_data()
        await self._fleet_manager.update_fleets_data()

    async def _check_channel_message(self):
        print('test')
        await self._bot_manager.chat_service.check_chat();
