from datetime import datetime, timedelta

from telegram.ext import MessageHandler, Application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext.filters import TEXT, COMMAND

from db.daos.channel_dao import ChannelDao
from db.daos.chat_dao import ChatDao
from models.chat_message_dto import ChatMessageDTO


class ChatService:
    def __init__(self, application: Application):
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
        if time_differece > timedelta(hours=1):
            # 更新消息
            await self._delete_message(channel_id, chat.message_id)
            await self._publish_message(channel_id)
        elif time_differece > timedelta(minutes=5) and not chat.is_newest:
            # 如果消息被覆盖，也更新消息
            await self._delete_message(channel_id, chat.message_id)
            await self._publish_message(channel_id)

    async def _delete_message(self, channel_id: int, message_id: int) -> None:
        try:
            await self._application.bot.delete_message(channel_id, message_id)
        except Exception as e:
            print('删除消息失败')

    async def _publish_message(self, channel_id: int) -> None:
        message = self._generate_message(channel_id)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('🎁 加入互推 🎁', self._application.bot.link)]])
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

        message = f'\n<b>{self._application.bot.first_name}</b>\n\n'
        for index, channel in enumerate(results):
            tmp = f'{index+1}. <b><a href="https://t.me/{channel.name}">{channel.title}</a></b>\n'
            message += tmp
        return message

    async def _handle_new_message(self, update, context):
        if not update.channel_post:
            return
        msg = update.channel_post
        channel_id = msg.chat_id
        ChatDao.set_message_invalidate(channel_id)
