from typing import Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from db.daos.user_dao import UserDao
from db.daos.fleet_dao import FleetDao


class ManageChannelStrategy(BaseButtonStrategy):
    def __init__(self, tag: str) -> None:
        super().__init__(tag)

    def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        channels = UserDao.get_user_channels(uid)

        message = '以下是您的频道信息，如数据出现异常，删除频道重新添加即可！'
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
                    tmp.append(InlineKeyboardButton(f'🚗 {fleet.name}', callback_data=f'{self.tag}#disable'))
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

    def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        if sub_target == 'no_access':
            return '当前频道没有赋予机器人有效权限，无法进行推车操作。请为机器人设置有效权限或者删除机器人后重新添加！'
        elif sub_target == 'is_banned':
            return '由于您的违规使用或数据作假，当前频道已被系统限制，将不能使用本推车功能！'
        elif sub_target == 'disable':
            pass
        elif sub_target == 'enable':
            pass
        elif sub_target == 'delete_channel':
            pass
