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

    async def get_message_and_buttons(self, target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        result = self._update_strategies(target)
        if result == None:
            return await self._handle_sub_operation(target, uid)
        else:
            return await result.get_message_and_buttons(uid)

    async def _handle_sub_operation(self, target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        # 处理子菜单操作
        strs = target.split('#')
        if strs == None or len(strs) < 2:
            return

        strategy = self._update_strategies(strs[0])

        if strategy == None:
            return '未知操作，请重试！'
        else:
            return await strategy.handle_operation(strs[1], uid)

    def _update_strategies(self, target):
        result = self._strategies.get(target)
        if result == None:
            if target == ButtonEnum.HOMEPAGE.value:
                result = HomepageStrategy(target, self._bot)
            elif target == ButtonEnum.MANAGE_CHANNEL.value:
                result = ManageChannelStrategy(target, self._bot)

            if result != None:
                self._strategies[target] = result
            else:
                return None

        return self._strategies[target]
