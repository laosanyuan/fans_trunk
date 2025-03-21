from typing import Union
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
import inject

from services.fleet_service import FleetService
from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy
from db.daos.fleet_dao import FleetDao
from db.daos.channel_dao import ChannelDao
from models.fleet_dto import FleetDTO
from models.channel_dto import ChannelDTO


class ManageFleetStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag)
        self._bot = bot

    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        keyboard = self._get_fleet_buttons()
        keyboard.append(self.get_home_button())
        markup = InlineKeyboardMarkup(keyboard)

        message = f'欢迎使用，以下是【{self._bot.first_name}】当前车队数据。\n点击对应车队按钮，可以查看车队详情！'
        message += '\n\n * 注意，本数据只代表当前情况，全部数据将随着用户的使用情况实时更新'

        return message, markup

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        strs = sub_target.split('%')
        if strs[0] == 'fleet':
            fleet_id = int(strs[1])
            fleet = FleetDao.get_fleet_by_id(fleet_id)
            channels = ChannelDao.get_fleet_chanels(fleet_id,15)
            if len(channels) < 30:
                # 数据真假各一半
                fakes = inject.instance(FleetService).get_fake_users(fleet.min_score,fleet.max_score,30-len(channels))
                channels.extend(fakes)
            random.shuffle(channels)
            return self._get_channel_list(fleet, channels), [self.get_preview_button]
        return '未知错误', [self.get_preview_button()]

    def _get_fleet_buttons(self)->list:
        fleets: list[FleetDTO] = FleetDao.get_all_fleets()
        results = []
        for item in fleets:
            results.append([InlineKeyboardButton(f'🚗 {item.name} ({item.channel_count})',callback_data=f'{self._tag}#fleets%{item.id}')])
        
        return results
    
    def _get_channel_list(self, fleet:FleetDTO, channels:list[ChannelDTO]) -> str:
        channel_count,member_count = inject.instance(FleetService).get_fleet_summary(fleet.id)
        text = f"欢迎查看 {fleet.name} 实时数据！\n\n"
        text += f"车队频道数量：{channel_count}\n车队成员数量：{member_count}\n车队准入评分范围：{fleet.min_score}~{fleet.max_score}/n/n"
        text += "为节约服务器资源提供更好的互推服务，此处查看车队信息每次最多仅随机获取车队中的30个频道数据用以参考：\n"
        for index, item in enumerate(channels):
            text += f'{index+1}. <b><a href="https://t.me/{item.name}">{item.title}</a></b>\n'
        return text

