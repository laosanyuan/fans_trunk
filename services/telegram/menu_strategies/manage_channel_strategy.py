from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.telegram.menu_strategies.base_strategy import BaseButtonStrategy, ButtonEnum
from db.daos.user_dao import UserDao


class ManageChannelStrategy(BaseButtonStrategy):
    def __init__(self, tag: str) -> None:
        super().__init__(tag)

    def get_message_and_buttons(self, uid: int) -> tuple[str, InlineKeyboardMarkup]:
        fleets = UserDao.get_user_fleets(uid)

        message = '以下是您的频道信息，如数据出现异常，删除频道重新添加即可！'
        buttons = []
        if fleets == None or len(fleets) <= 0:
            message = '您还没有添加任何频道，请返回首页添加频道后再查看！'
        else:
            for item in fleets:
                tmp = [InlineKeyboardButton(item.title, url=f'https://t.me/{item.name}')]
                if item.is_access:
                    if item.is_enable:
                        tmp.append(InlineKeyboardButton('退出车队', callback_data=f'{self.tag}#disable'))
                    else:
                        tmp.append(InlineKeyboardButton('加入车队', callback_data=f'{self.tag}#enable'))
                else:
                    if item.is_banned:
                        tmp.append(InlineKeyboardButton('频道被封禁', callback_data=f'{self.tag}#is_banned'))
                    else:
                        tmp.append(InlineKeyboardButton('频道权限不足', callback_data=f'{self.tag}#no_access'))

                tmp.append(InlineKeyboardButton('删除', callback_data=f'{self.tag}#delete_channel'))
                buttons.append(tmp)

        buttons.append([InlineKeyboardButton('返回首页', callback_data=ButtonEnum.HOMEPAGE.value)])

        if len(buttons) == 0:
            return message, None
        else:
            return message, InlineKeyboardMarkup(buttons)

    def handle_operation(self, sub_target: str) -> None:
        if sub_target == 'no_access':
            pass
        elif sub_target == 'is_banned':
            pass
        elif sub_target == 'diable':
            pass
        elif sub_target == 'enable':
            pass
        elif sub_target == 'delete_channel':
            pass
