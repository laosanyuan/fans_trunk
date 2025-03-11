from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from db.daos.user_dao import UserDao
from db.daos.fleet_dao import FleetDao
from db.daos.channel_dao import ChannelDao


class ManageChannelStrategy(BaseButtonStrategy):
    def __init__(self, tag: str, bot: Bot) -> None:
        super().__init__(tag)
        self._bot = bot

    async def get_message_and_buttons(self,
                                      uid: int,
                                      message='以下是您的频道信息，如数据出现异常，删除频道重新添加即可！') -> Union[tuple[str, InlineKeyboardMarkup], str]:
        channels = UserDao.get_user_channels(uid)

        buttons = []
        if channels == None or len(channels) <= 0:
            message = '您还没有添加任何频道，请返回首页添加频道后再查看！'
        else:
            for item in channels:
                tmp = []
                flag = ""
                if item.is_banned:
                    flag = '🔴'
                    tmp.append(InlineKeyboardButton('🚫 审核不通过', callback_data=f'{self.tag}#is_banned'))
                elif item.is_access:
                    flag = '🟢'
                    fleet = FleetDao.get_fleet_by_id(item.fleet_id)
                    tmp.append(InlineKeyboardButton(f'🚗 {fleet.name}', callback_data=f'{self.tag}#running%{item.fleet_id}'))
                else:
                    flag = '🟡'
                    tmp.append(InlineKeyboardButton('💔 权限不足', callback_data=f'{self.tag}#no_access'))

                name = f'{flag} {item.title}'
                tmp.insert(0, InlineKeyboardButton(name, url=f'https://t.me/{item.name}'))
                tmp.append(InlineKeyboardButton('🗑️ 删除', callback_data=f'{self.tag}#delete_channel%{item.id}'))
                buttons.append(tmp)

        buttons.append([InlineKeyboardButton('🏡 返回首页', callback_data=ButtonEnum.HOMEPAGE.value)])

        if len(buttons) == 0:
            return message, None
        else:
            return message, InlineKeyboardMarkup(buttons)

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        if sub_target == 'no_access':
            return '当前频道没有赋予机器人有效权限，无法进行推车操作。请为机器人设置有效权限或者删除机器人后重新添加！'
        elif sub_target == 'is_banned':
            return '由于您的违规使用或数据作假，当前频道已被系统限制，将不能使用本推车功能！'
        else:
            strs = sub_target.split('%')
            if strs[0] == 'running':
                fleet = FleetDao.get_fleet_by_id(int(strs[1]))
                return f'当前频道整运行于{fleet.name}，本车队覆盖频道数：{fleet.all_channel_count}，曝光覆盖总成员数约为：{fleet.all_fans_count}'
            elif strs[0] == 'delete_channel':
                channel_id = int(strs[1])
                ChannelDao.remove_channel(channel_id)
                await self._bot.leave_chat(channel_id)
                return self.get_message_and_buttons(uid, '频道删除成功，以下是更新后的频道列表（如果频道数据存在错误，可删除后重新添加）：')
