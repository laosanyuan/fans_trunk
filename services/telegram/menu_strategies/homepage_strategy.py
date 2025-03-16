from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from db.daos.fleet_dao import FleetDao


class HomepageStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag)
        self._bot = bot

    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        keyboard = [
            [InlineKeyboardButton("🔥 添加机器人到频道", url=f'{self._bot.link}?startchannel&admin=post_messages+edit_messages+delete_messages+invite_users'),
             InlineKeyboardButton("🫰 管理我的频道", callback_data=ButtonEnum.MANAGE_CHANNEL.value)],
            [InlineKeyboardButton("🚛 查看车队信息", callback_data=ButtonEnum.VIEW_FLEETS.value)]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        channel_count, member_count = FleetDao.get_channel_summary()
        message = f'''
✨ 欢迎使用【{self._bot.first_name}】——您的频道增长智能管家！
🔥 精准流量匹配 | 公平透明机制 | 7×24小时护航

🚀 当前频道数量：{channel_count}
🚀 覆盖用户数量：{member_count}

点击 /help 命令查看帮助指引

🚫<b>严谨发布幼童/人兽/男同/血腥/暴力/重口/政治/军火 等内容‼️</b>

👇点击底部菜单按钮选择功能👇
'''

        return message, markup

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        return self.get_message_and_buttons(uid)
