import traceback
import platform
import os
import sys
import asyncio

import inject

from services.config_parser import ConfigParser
from services.wxpusher_service import WxPusherService
from services.scheduler_service import SchedulerService
from services.fleet_service import FleetService
from services.telegram_service import TelegramService
from db.db_service import DbService


def global_exception_handler(exctype, value, tb):
    if exctype == SystemExit:
        return
    error_message = f"Exception Type: {exctype}\nMessage: {value}\nTraceback: {traceback.format_exc()}"
    inject.instance(WxPusherService).push('Telegram推送服务崩溃', error_message)


def define_bindings(binder: inject.Binder):
    binder.bind(ConfigParser, ConfigParser('configs/settings.json'))
    binder.bind(FleetService, FleetService('configs/fleets.json'))
    binder.bind_to_constructor(WxPusherService, WxPusherService)
    binder.bind_to_constructor(SchedulerService, SchedulerService)
    binder.bind_to_constructor(TelegramService, TelegramService)
    binder.bind(DbService, DbService("./configs/data.db"))


def main_method():
    # 启动时执行
    inject.configure(define_bindings)

    # 设置代理
    if platform.system() == 'Windows':
        # 处于开发环境
        proxy = inject.instance(ConfigParser).get_proxy()
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy

    try:
        inject.instance(DbService).init_db()
        asyncio.run(inject.instance(SchedulerService).start())
        asyncio.run(inject.instance(TelegramService).start())
    except KeyboardInterrupt:
        print("程序被手动终止")
    except Exception as e:
        print(f"发生异常: {e}")
    finally:
        inject.instance(DbService).close_db()
        inject.instance(SchedulerService).stop()


if __name__ == '__main__':
    sys.excepthook = global_exception_handler
    main_method()
