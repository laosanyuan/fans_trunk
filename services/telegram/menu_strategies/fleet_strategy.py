from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from db.daos.fleet_dao import FleetDao
from models.fleet_dto import FleetDTO


class FleetStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag)
        self._bot = bot

    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        keyboard = []
        keyboard.append([InlineKeyboardButton('🏡 返回首页', callback_data=ButtonEnum.HOMEPAGE.value)])
        markup = InlineKeyboardMarkup(keyboard)

        message = f'欢迎使用，以下是【{self._bot.first_name}】当前车队数据：'
        message += self._get_fleets_html()
        message += '\n\n * 注意，本数据只代表当前情况，全部数据将随着用户的使用情况实时更新'

        return message, markup

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        return self.get_message_and_buttons(uid)

    def _get_fleets_html(self):
        fleets: list[FleetDTO] = FleetDao.get_all_fleets()

        text = ''
        for fleet in fleets:
            tmp = f'\n\n🚗 <b>{fleet.name}</b>\n'
            tmp += f'当前频道数量：{fleet.channel_count}\n'
            tmp += f'覆盖成员数量：{fleet.member_count}'
            text += tmp
        return text
