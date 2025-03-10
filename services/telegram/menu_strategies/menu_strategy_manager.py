from telegram import Bot

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from services.telegram.menu_strategies.manage_channel_strategy import ManageChannelStrategy
from services.telegram.menu_strategies.homepage_strategy import HomepageStrategy


class MenuStrategyManager:
    def __init__(self) -> None:
        self._strategies = dict()

    def get_strategy(self, target: str, bot: Bot) -> BaseButtonStrategy:
        strategy = None

        if target == ButtonEnum.HOMEPAGE.value:
            result = self._strategies.get(target)
            if result is None:
                self._strategies[target] = HomepageStrategy(target, bot)
            strategy = self._strategies[target]
        if target == ButtonEnum.MANAGE_CHANNEL.value:
            result = self._strategies.get(target)
            if result is None:
                self._strategies[target] = ManageChannelStrategy(target)
            strategy = self._strategies[target]

        return strategy

    def handle_sub_operation(self, target: str, bot: Bot) -> None:
        # 处理子菜单操作
        strs = target.split('#')
        if strs == None or len(strs) < 2:
            return

        strategy = self._strategies[strs[0]]
        strategy.handle_operation(strs[1])
