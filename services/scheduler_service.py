import asyncio

from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import inject

from services.wxpusher_service import WxPusherService


class SchedulerService:
    @inject.autoparams()
    def __init__(self, wx_pusher: WxPusherService):
        self._wx_pusher = wx_pusher

        self._scheduler = AsyncIOScheduler()

        # 日报
        self._scheduler.add_job(self._post_daily_report,
                                CronTrigger(hour=22, timezone=timezone("Asia/Shanghai")))
        # 每日数据更新
        self._scheduler.add_job(self._update_daily_data,
                                CronTrigger(hour=2, timezone=timezone("Asia/Shanghai")))
        # 评级更新
        self._scheduler.add_job(self._update_score,
                                IntervalTrigger(hours=1),
                                max_instances=1)
        # 检查频道消息
        self._scheduler.add_job(self._check_channel_message,
                                IntervalTrigger(hours=1),
                                max_instances=1)

    async def start(self):
        """启动调度器"""
        self._scheduler.start()

    def stop(self):
        """停止调度器"""
        if self._scheduler.state == 1:
            self._scheduler.pause()

    def _post_daily_report(self):
        pass

    def _update_daily_data(self):
        pass

    def _update_score(self):
        pass

    def _check_channel_message(self):
        pass
