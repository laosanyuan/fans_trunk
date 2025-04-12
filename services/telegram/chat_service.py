from datetime import datetime, timedelta
import asyncio

from telegram.ext import MessageHandler, Application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext.filters import TEXT, COMMAND
import inject

from db.daos.channel_dao import ChannelDao
from db.daos.chat_dao import ChatDao
from models.chat_message_dto import ChatMessageDTO
from services.ad_service import AdService, AdConfig
from services.channel_data_provider import ChannelDataProvider


class ChatService:
    def __init__(self, application: Application):
        self._channel_data_provider = inject.instance(ChannelDataProvider)
        self._application = application
        self._application.add_handler(MessageHandler(TEXT & (~COMMAND), self._handle_new_message))

    async def check_chat(self):
        channels = ChannelDao.get_all_validate_channels()
        for item in channels:
            # 是否已存在消息
            if ChatDao.is_exists(item.id):
                await self._update_chat(item.id)
            else:
                await self._publish_message(item.id)

    async def _update_chat(self, channel_id: int) -> bool:
        chat: ChatMessageDTO = ChatDao.get_chat_message(channel_id)
        time_differece = datetime.now() - chat.push_time
        is_more_than_hour = time_differece > timedelta(hours=1)
        is_not_newest = (time_differece > timedelta(minutes=10) and not chat.is_newest)
        if is_more_than_hour or is_not_newest:
            # 超过1小时或者超过10分钟存在新消息覆盖，则更新消息
            await self._delete_message(channel_id, chat.message_id)
            await self._publish_message(channel_id)
            await asyncio.sleep(1)

    async def _delete_message(self, channel_id: int, message_id: int) -> None:
        try:
            await self._application.bot.delete_message(channel_id, message_id)
        except Exception as e:
            print('删除消息失败')
            print(e.with_traceback)
            ChatDao.delete_message(channel_id)

    async def _publish_message(self, channel_id: int) -> None:
        ad_service = inject.instance(AdService)
        body = self._generate_message(channel_id)
        if body == None or body == '':
            print('发车频道数量不足')
            return
        # 文案部分
        fleet_name = f'\n<b>{self._application.bot.first_name}</b> - 精彩推送'
        head_ad = self._get_ad_message(ad_service.head_ads)
        tail_ad = self._get_ad_message(ad_service.tail_ads)
        message = f'{fleet_name}\n{head_ad}\n{body}\n{tail_ad}'

        # 按钮部分
        button_list = []
        for ad in ad_service.button_ads:
            button_list.append([InlineKeyboardButton(ad.text, ad.link)])
        button_list.append([InlineKeyboardButton('🎁 加入互推 🎁', self._application.bot.link)])
        markup = InlineKeyboardMarkup(button_list)

        result = await self._application.bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode='HTML',
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=60,
            read_timeout=60,
            disable_web_page_preview=True,
            reply_markup=markup)

        ChatDao.update_publish_message(channel_id, result.message_id)

    def _generate_message(self, channel_id) -> str:
        results = ChannelDao.get_message_channels(channel_id)

        if len(results) <= 3:
            # 如果有效频道太少，使用假数据补充
            fleet = ChannelDao.get_channel_fleet(channel_id)
            results += self._channel_data_provider.get_fake_users(fleet.min_score, fleet.max_score, 5)

        message = ''
        for index, channel in enumerate(results):
            tmp = f'{index+1}. <b><a href="https://t.me/{channel.name}">{channel.title}</a></b>\n'
            message += tmp
        return message

    def _get_ad_message(self, ads: list[AdConfig]) -> None:
        message = ''
        for ad in ads:
            tmp = f'<b>AD: <a href="{ad.link}">{ad.text}</a></b>\n'
            message += tmp
        return message

    async def _handle_new_message(self, update, context):
        if not update.channel_post:
            return
        msg = update.channel_post
        channel_id = msg.chat_id
        ChatDao.set_message_invalidate(channel_id)
