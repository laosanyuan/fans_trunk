import traceback
import platform
import os
import sys
import asyncio

import inject
import nest_asyncio

from db.db_service import DbService
from services.config_parser import ConfigParser
from services.wxpusher_service import WxPusherService
from services.scheduler_manager import SchedulerManager
from services.fleet_manager import FleetManager
from services.telegram.bot_manager import BotManager
from services.ad_service import AdService
from services.fleet_service import FleetService

def global_exception_handler(exctype, value, tb):
    if exctype == SystemExit:
        return
    error_message = f"Exception Type: {exctype}\nMessage: {value}\nTraceback: {traceback.format_exc()}"
    inject.instance(WxPusherService).push('Telegram推送服务崩溃', error_message)


def define_bindings(binder: inject.Binder):
    binder.bind(ConfigParser, ConfigParser('configs/settings.json'))
    binder.bind_to_constructor(WxPusherService, WxPusherService)
    binder.bind_to_constructor(BotManager, BotManager)
    binder.bind(DbService, DbService("./configs/data.db"))
    binder.bind(FleetManager, FleetManager('configs/fleets.json'))
    binder.bind_to_constructor(SchedulerManager, SchedulerManager)
    binder.bind(AdService, AdService('./configs/ad_settings.json'))
    binder.bind(FleetService, FleetService('./configs/fake_users.json'))


async def main():
    inject.configure(define_bindings)

    if platform.system() == 'Windows':
        # 处于开发环境
        proxy = inject.instance(ConfigParser).get_proxy()
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy

    try:
        inject.instance(DbService).init_db()
        inject.instance(FleetManager).init()

        scheduler_manager = inject.instance(SchedulerManager)
        bot_manager = inject.instance(BotManager)

        scheduler_manager.start()
        await bot_manager.run()

        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("程序被手动终止")
    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        inject.instance(DbService).close_db()
        inject.instance(SchedulerManager).stop()

if __name__ == '__main__':
    nest_asyncio.apply()
    sys.excepthook = global_exception_handler
    asyncio.run(main())
