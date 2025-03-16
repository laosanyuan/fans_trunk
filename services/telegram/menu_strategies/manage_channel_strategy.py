from typing import Union
import math

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
                                      page=0,
                                      message='以下是您的频道信息，如数据出现异常，删除频道重新添加即可！') -> Union[tuple[str, InlineKeyboardMarkup], str]:
        channel_page = UserDao.get_user_channels(uid, page)

        buttons = []
        if channel_page == None or channel_page.total <= 0:
            message = '您还没有添加任何频道到车队，请添加频道后再查看！'
            buttons.append([InlineKeyboardButton(
                "🔥 添加机器人到频道", url=f'{self._bot.link}?startchannel&admin=post_messages+edit_messages+delete_messages+invite_users')])
        else:
            # 添加频道数据
            for item in channel_page.channels:
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

            # 添加翻页按钮
            message += f'\n\n您的频道数量：{channel_page.total}\n当前正处于第【{channel_page.page+1}/{math.ceil(channel_page.total/channel_page.page_size)}】页'
            page_buttons = []
            if not channel_page.is_first:
                page_buttons.append(InlineKeyboardButton('👆 上一页', callback_data=f'{self.tag}#page%{channel_page.page-1}'))
            if not channel_page.is_last:
                page_buttons.append(InlineKeyboardButton('👇 下一页', callback_data=f'{self.tag}#page%{channel_page.page+1}'))
            buttons.append(page_buttons)

        buttons.append([InlineKeyboardButton('🏡 返回首页', callback_data=ButtonEnum.HOMEPAGE.value)])

        if len(buttons) == 0:
            return message, None
        else:
            return message, InlineKeyboardMarkup(buttons)

    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        if sub_target == 'no_access':
            return '当前频道没有赋予机器人有效权限，无法进行推车操作。请为机器人设置有效权限或者删除机器人后重新添加！'
        elif sub_target == 'is_banned':
            return '由于您的违规使用或数据作弊，当前频道已被系统限制，将不能使用本推车功能！'
        else:
            strs = sub_target.split('%')
            if strs[0] == 'running':
                # 查看频道信息
                fleet = FleetDao.get_fleet_by_id(int(strs[1]))
                return f'当前频道整运行于{fleet.name}，本车队覆盖频道数：{fleet.channel_count}，曝光覆盖总成员数约为：{fleet.member_count}'
            elif strs[0] == 'delete_channel':
                # 删除频道
                channel_id = int(strs[1])
                ChannelDao.remove_channel(channel_id)
                await self._bot.leave_chat(channel_id)
                return await self.get_message_and_buttons(uid, message='频道删除成功，以下是更新后的频道列表（如果频道数据存在错误，可删除后重新添加）：')
            elif strs[0] == 'page':
                # 翻页
                return await self.get_message_and_buttons(uid, page=int(strs[1]))
