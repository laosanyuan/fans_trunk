from datetime import datetime, timedelta
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import Application, MessageHandler
from telegram.ext.filters import COMMAND, TEXT
import inject

from db.daos.channel_dao import ChannelDao
from db.daos.chat_dao import ChatDao
from models.chat_message_dto import ChatMessageDTO
from services.ad_service import AdConfig, AdService
from services.channel_data_provider import ChannelDataProvider


class ChatService:
    def __init__(self, application: Application):
        self._channel_data_provider = inject.instance(ChannelDataProvider)
        self._application = application
        self._application.add_handler(MessageHandler(TEXT & (~COMMAND), self._handle_new_message))
        self._delete_channel_cache: dict[int, datetime] = {}

    async def check_chat(self):
        channels = ChannelDao.get_all_validate_channels()
        for item in channels:
            if ChatDao.is_exists(item.id):
                await self._update_chat(item.id)
            else:
                await self._publish_message(item.id)

    async def _update_chat(self, channel_id: int) -> None:
        chat: ChatMessageDTO = ChatDao.get_chat_message(channel_id)
        time_difference = datetime.now() - chat.push_time
        is_more_than_hour = time_difference > timedelta(hours=1)
        is_not_newest = time_difference > timedelta(minutes=10) and not chat.is_newest
        if is_more_than_hour or is_not_newest:
            is_deleted = await self._delete_message(channel_id, chat.message_id)
            if not is_deleted:
                return

            await self._publish_message(channel_id)
            await asyncio.sleep(1)

    async def _delete_message(self, channel_id: int, message_id: int) -> bool:
        try:
            await self._application.bot.delete_message(channel_id, message_id)
            self._reset_channel_cache(channel_id)
            return True
        except BadRequest:
            if not self._can_delete_channel(channel_id):
                self._mark_channel_delete_pending(channel_id)
                return False

            channel = ChannelDao.get_channel(channel_id)
            print(f'频道已不存在:{channel.title}，移出列表')
            ChannelDao.remove_channel(channel_id)
            self._clear_delete_channel_cache(channel_id)
            return False
        except Exception as exc:
            print('删除消息失败')
            print(exc)
            ChatDao.delete_message(channel_id)
            return False

    async def _publish_message(self, channel_id: int) -> None:
        ad_service = inject.instance(AdService)
        body = self._generate_message(channel_id)
        if not body:
            print('发车频道数量不足')
            return

        fleet_name = f'\n<b>{self._application.bot.first_name}</b> - 精彩推送'
        head_ad = self._get_ad_message(ad_service.head_ads)
        tail_ad = self._get_ad_message(ad_service.tail_ads)
        message = f'{fleet_name}\n{head_ad}\n{body}\n{tail_ad}'

        button_list = []
        for ad in ad_service.button_ads:
            button_list.append([InlineKeyboardButton(ad.text, ad.link)])
        button_list.append([InlineKeyboardButton('🎁 加入互推 🎁', self._application.bot.link)])
        markup = InlineKeyboardMarkup(button_list)

        try:
            result = await self._application.bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode='HTML',
                write_timeout=60,
                connect_timeout=60,
                pool_timeout=60,
                read_timeout=60,
                disable_web_page_preview=True,
                reply_markup=markup
            )
            ChatDao.update_publish_message(channel_id, result.message_id)
            self._reset_channel_cache(channel_id)
        except Forbidden:
            await self._remove_channel_with_notice(
                channel_id,
                '您的频道【{title}】由于权限错误，无法发送互推消息！如果需要继续使用，您可以重新拉入机器人并设置正确权限恢复功能！'
            )
        except BadRequest:
            if not self._can_delete_channel(channel_id):
                self._mark_channel_delete_pending(channel_id)
                return

            channel = ChannelDao.get_channel(channel_id)
            print(f'频道已不存在:{channel.title}，移出列表')
            ChannelDao.remove_channel(channel_id)
            self._clear_delete_channel_cache(channel_id)
        except Exception:
            await self._remove_channel_with_notice(
                channel_id,
                '您的频道【{title}】由于发布推送消息失败，暂时移出车队。原因可能为权限错误，您可以重新拉入机器人并设置正确权限恢复功能！'
            )

    async def _remove_channel_with_notice(self, channel_id: int, message_template: str) -> None:
        channel = ChannelDao.get_channel(channel_id)
        try:
            await self._application.bot.send_message(
                chat_id=channel.user_id,
                text=message_template.format(title=channel.title),
                parse_mode=ParseMode.HTML
            )
        except Exception as exc:
            print('通知用户失败')
            print(exc)
        finally:
            ChannelDao.remove_channel(channel_id)
            self._clear_delete_channel_cache(channel_id)

    def _generate_message(self, channel_id: int) -> str:
        results = ChannelDao.get_message_channels(channel_id)
        message = ''
        for index, channel in enumerate(results):
            message += f'{index + 1}. <b><a href="https://t.me/{channel.name}">{channel.title}</a></b>\n'
        return message

    def _get_ad_message(self, ads: list[AdConfig]) -> str:
        message = ''
        for ad in ads:
            message += f'<b>AD: <a href="{ad.link}">{ad.text}</a></b>\n'
        return message

    async def _handle_new_message(self, update, context):
        if not update.channel_post:
            return

        channel_id = update.channel_post.chat_id
        ChatDao.set_message_invalidate(channel_id)

    def _reset_channel_cache(self, channel_id: int) -> None:
        self._delete_channel_cache.pop(channel_id, None)

    def _mark_channel_delete_pending(self, channel_id: int) -> None:
        self._delete_channel_cache.setdefault(channel_id, datetime.now())

    def _clear_delete_channel_cache(self, channel_id: int) -> None:
        self._delete_channel_cache.pop(channel_id, None)

    def _can_delete_channel(self, channel_id: int) -> bool:
        if channel_id not in self._delete_channel_cache:
            return False

        if datetime.now() - self._delete_channel_cache[channel_id] >= timedelta(hours=36):
            print(f'删除延时缓存已超过36小时:{channel_id}')
            self._clear_delete_channel_cache(channel_id)
            return True
        return False
