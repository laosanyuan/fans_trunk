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
        chat: ChatMessageDTO = ChatDao.get_push_time(channel_id)
        time_differece = datetime.now - chat.push_time
        if time_differece > timedelta(60):
            # 更新消息
            self._delete_chat(channel_id)
            self._publish_chat(channel_id)
        elif time_differece > timedelta(5) and not self._is_chat_newest(channel_id):
            # 如果消息被覆盖，也更新消息
            self._delete_chat(channel_id)
            self._publish_chat(channel_id)

    async def _delete_chat(self, channel_id: int) -> None:
        pass

    async def _is_chat_newest(self, channel_id) -> bool:
        return True

    async def _publish_chat(self, channel_id: int) -> None:
        message = self._generate_message(channel_id)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('🎁 加入互推 🎁', self._application.bot.link)]])
        result = await self._application.bot.send_message(
            f"@{channel_id}",
            text=message,
            parse_mode='HTML',
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=60,
            read_timeout=60,
            reply_markup=markup)

        message_id = result
        pass

    def _generate_message(self, channel_id) -> str:
        return "test"
