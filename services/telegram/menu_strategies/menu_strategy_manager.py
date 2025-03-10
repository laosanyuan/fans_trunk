from typing import Union

from telegram import Bot
from telegram import InlineKeyboardMarkup

from services.telegram.menu_strategies.base_strategy import ButtonEnum
from services.telegram.menu_strategies.manage_channel_strategy import ManageChannelStrategy
from services.telegram.menu_strategies.homepage_strategy import HomepageStrategy


class MenuStrategyManager:
    def __init__(self, bot: Bot) -> None:
        self._strategies = dict()
        self._bot = bot

    def get_message_and_buttons(self, target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        result = self._strategies.get(target)
        if result == None:
            if target == ButtonEnum.HOMEPAGE.value:
                result = HomepageStrategy(target, self._bot)
            elif target == ButtonEnum.MANAGE_CHANNEL.value:
                result = ManageChannelStrategy(target)

            if result != None:
                self._strategies[target] = result

        if result == None:
            return self._handle_sub_operation(target, uid)
        else:
            return result.get_message_and_buttons(uid)

    def _handle_sub_operation(self, target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        # 处理子菜单操作
        strs = target.split('#')
        if strs == None or len(strs) < 2:
            return

        strategy = self._strategies[strs[0]]
        return strategy.handle_operation(strs[1], uid)
