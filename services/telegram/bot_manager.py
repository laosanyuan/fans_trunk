import asyncio

from telegram.ext import ApplicationBuilder
import inject

from services.config_parser import ConfigParser
from services.telegram.menu_strategies.menu_strategy_manager import MenuStrategyManager
from services.telegram.user_service import UserService
from services.telegram.admin_service import AdminService
from services.telegram.chat_service import ChatService

class BotManager:
    @inject.autoparams()
    def __init__(self, config_parser: ConfigParser):
        self._token = config_parser.get_bot_token()
        self._menu_strategy_manager = MenuStrategyManager()

        self._application = ApplicationBuilder().token(self._token).build()

        self._user_service = UserService(self._application)
        self._admin_service = AdminService(self._application)
        self._chat_service = ChatService(self._chat_service)


    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._application.run_polling(close_loop=False)