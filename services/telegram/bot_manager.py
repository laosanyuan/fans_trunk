import asyncio
import threading

from telegram.ext import ApplicationBuilder
import inject

from services.config_parser import ConfigParser
from services.telegram.user_service import UserService
from services.telegram.admin_service import AdminService
from services.telegram.chat_service import ChatService


class BotManager:
    @inject.autoparams()
    def __init__(self, config_parser: ConfigParser):
        self._token = config_parser.get_bot_token()

        self._application = ApplicationBuilder().token(self._token).build()

        self.user_service = UserService(self._application)
        self.admin_service = AdminService(self._application)
        self.chat_service = ChatService(self._application)

    async def run(self):
        # 启动 run_polling 在一个单独的线程中
        def run_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._application.run_polling(close_loop=False)

        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

        # 等待线程启动
        while not bot_thread.is_alive():
            await asyncio.sleep(0.1)
