from datetime import datetime, timedelta

from telegram.ext import Application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


from db.daos.channel_dao import ChannelDao
from db.daos.chat_dao import ChatDao
from models.chat_message_dto import ChatMessageDTO


class ChatService:
    def __init__(self, application: Application):
        self._application = application

    async def check_chat(self):
        channels = ChannelDao.get_all_validate_channels()
        for item in channels:
            # 是否已存在消息
            if ChatDao.is_exists(item.id):
                await self._update_chat(item.id)
            else:
                await self._publish_chat(item.id)

    async def _update_chat(self, channel_id: int) -> bool:
        chat: ChatMessageDTO = ChatDao.get_chat_message(channel_id)
        time_differece = datetime.now() - chat.push_time
        if time_differece > timedelta(hours=1):
            # 更新消息
            self._delete_chat(channel_id)
            self._publish_chat(channel_id)
        elif time_differece > timedelta(minutes=1) and not await self._is_chat_newest(channel_id):
            # 如果消息被覆盖，也更新消息
            self._delete_chat(channel_id)
            self._publish_chat(channel_id)
            print('更新消息')

    async def _delete_chat(self, channel_id: int) -> None:
        message_id = ChatDao.get_message_id(channel_id)
        await self._application.bot.delete_message(channel_id, message_id)

    async def _is_chat_newest(self, channel_id) -> bool:
        message_id = ChatDao.get_message_id(channel_id)
        messages = await self._application.bot.get_chat_history(chat_id=channel_id, limit=1)
        if messages and messages[0].message_id == message_id:
            return True
        else:
            return False

    async def _publish_chat(self, channel_id: int) -> None:
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
            reply_markup=markup)

        ChatDao.update_message(channel_id, result.message_id)

    def _generate_message(self, channel_id) -> str:
        return "test"
