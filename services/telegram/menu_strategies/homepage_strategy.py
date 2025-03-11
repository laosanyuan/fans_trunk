from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum


class HomepageStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag)
        self._bot = bot

    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        keyboard = [
            [InlineKeyboardButton("🔥 添加机器人到频道", url=f'{self._bot.link}?startchannel&admin=post_messages+edit_messages+delete_messages+invite_users'),
             InlineKeyboardButton("🫰 管理我的频道", callback_data=ButtonEnum.MANAGE_CHANNEL.value)],
            [InlineKeyboardButton("🚛 查看车队信息", callback_data=ButtonEnum.VIEW_FLEETS.value)],
            [InlineKeyboardButton("📜 查看运行规则", callback_data=ButtonEnum.VIEW_RULES.value)]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        message = f'欢迎使用【{self._bot.name}】！'

        return message, markup

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        return self.get_message_and_buttons(uid)
