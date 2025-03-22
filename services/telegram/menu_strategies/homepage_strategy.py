from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
import inject

from services.channel_data_provider import ChannelDataProvider
from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum


class HomepageStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag, bot)

    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        keyboard = [
            [self.get_add_channel_button(), InlineKeyboardButton("🫰 管理我的频道", callback_data=ButtonEnum.MANAGE_CHANNEL.value)],
            [InlineKeyboardButton("🚛 查看车队信息", callback_data=ButtonEnum.VIEW_FLEETS.value)]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        channel_count, member_count = inject.instance(ChannelDataProvider).get_all_summary()
        message = f'''
✨ 欢迎使用【{self.bot.first_name}】——您的频道增长智能管家！
🔥 精准流量匹配 | 公平透明机制 | 7×24小时护航

🚀 当前频道数量：{channel_count}
🚀 覆盖用户数量：{member_count}

<b>本机器人简化流程，添加频道即上车，无需复杂选车操作！！！</b>
<b>本机器人简化流程，添加频道即上车，无需复杂选车操作！！！</b>
<b>本机器人简化流程，添加频道即上车，无需复杂选车操作！！！</b>

点击 /help 命令查看帮助指引

🚫<b>严谨发布幼童/人兽/男同/血腥/暴力/重口/政治/军火 等内容‼️</b>

👇点击底部菜单按钮选择功能👇
'''

        return message, markup

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        return self.get_message_and_buttons(uid)
