from telegram.ext import Application

from services.telegram.menu_strategies.menu_strategy_manager import MenuStrategyManager


class AdminService:
    def __init__(self, application: Application):
        self._menu_strategy_manager = MenuStrategyManager()
        self._application = application