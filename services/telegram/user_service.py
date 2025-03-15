import asyncio

from telegram import Update, ChatMemberUpdated
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, ChatMemberHandler, Application
from telegram.constants import ChatMemberStatus, ParseMode
import inject

from services.telegram.menu_strategies.menu_strategy_manager import MenuStrategyManager, ButtonEnum
from services.score_service import ScoreService
from db.daos.user_dao import UserDao
from db.daos.channel_dao import ChannelDao
from db.daos.fleet_dao import FleetDao


class UserService:
    def __init__(self, application: Application):
        self._application = application
        self._menu_strategy_manager = MenuStrategyManager(self._application.bot)
        self._score_service = inject.instance(ScoreService)

        self._application.add_handler(CallbackQueryHandler(self._button_callback))
        self._application.add_handler(CommandHandler('start', self._start_command))
        self._application.add_handler(CommandHandler('help', self._help_command))
        self._application.add_handler(ChatMemberHandler(self._track_chat_member, ChatMemberHandler.ANY_CHAT_MEMBER))

    async def update_all_user_data(self):
        channels = ChannelDao.get_all_validate_channels()
        for channel in channels:
            member_count = await self._application.bot.get_chat_member_count(channel.id)
            view_count = 0.05*member_count
            score = self._score_service.get_score(member_count, view_count)
            fleet = FleetDao.get_fleet_by_score(score)
            ChannelDao.update_member_count(member_count, fleet.id)
            await asyncio.sleep(1)

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        user_name = update.effective_user.username
        full_name = update.effective_user.full_name
        UserDao.add_user(uid=uid, user_name=user_name, full_name=full_name)

        message, reply_markup = await self._menu_strategy_manager.get_message_and_buttons(ButtonEnum.HOMEPAGE.value, uid)

        await update.message.reply_text(message, reply_markup=reply_markup)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        callback_data = query.data
        uid = query.from_user.id
        result = await self._menu_strategy_manager.get_message_and_buttons(callback_data, uid)

        if isinstance(result, str):
            await query.answer(text=result, cache_time=3)
        elif isinstance(result, tuple):
            await query.edit_message_text(
                text=result[0],
                reply_markup=result[1],
                parse_mode=ParseMode.HTML)

    async def _track_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 处理添加移除机器人
        chat_member: ChatMemberUpdated = update.my_chat_member
        status = chat_member.new_chat_member.status
        uid = chat_member.from_user.id
        channel_id = chat_member.chat.id
        channel_name = chat_member.chat.username
        channel_title = chat_member.chat.title

        if status == ChatMemberStatus.ADMINISTRATOR:
            message = ''
            has_permission = await self._check_permissions(channel_id)
            if ChannelDao.is_exists(channel_id):
                ChannelDao.update_permission(channel_id, has_permission)
                if has_permission:
                    message = f'✅ 频道【{channel_title}】机器人权限发生变更，当前权限有效，频道发车中！'
                else:
                    message = f'🚫 频道【{channel_title}】机器人权限发生变更，机器人时失去频道发车权限，请重新赋予正确权限后恢复发车！'
            else:
                member_count = await self._application.bot.get_chat_member_count(channel_id)
                # 暂未实现获取浏览量
                view_count = 0.05*member_count
                score = self._score_service.get_score(member_count, view_count)
                fleet = FleetDao.get_fleet_by_score(score)

                ChannelDao.add_channel(uid, channel_id, channel_name, channel_title, fleet.id, has_permission, member_count)
                FleetDao.update_fleets_data()

                if has_permission:
                    message = f'''🎉 恭喜您，添加频道成功！

系统根据您的频道数据智能评级，【<b>{channel_title}</b>】当前的得分为<b>{score}</b>，分配于<b>{fleet.name}</b>，本车队包含频道数量：<b>{fleet.channel_count}</b>，合计覆盖成员数量：<b>{fleet.member_count}</b>！

注意，当前的评分和分配车队都是基于此频道目前的数据计算得出，随着数据的变化，评分和分配车队随时也会随时发生变化。

✈ 祝大哥发财，马上发车！'''
                else:
                    message = f'🚫 频道【{channel_title}】添加成功，但当前缺少运行权限无法运行，请赋予必要权限或删除后重新添加。\n\n机器人需要获得必要操作权限，然后才能发车！'

            await context.bot.send_message(
                chat_id=uid,
                text=message,
                parse_mode=ParseMode.HTML
            )
        elif status == ChatMemberStatus.LEFT or status == ChatMemberStatus.BANNED or ChatMemberStatus.RESTRICTED:
            if not ChannelDao.is_exists(channel_id):
                # 频道数据不存在可能为主动删除
                return

            ChannelDao.remove_channel(channel_id)
            message = f'您的频道【{channel_title}】已失去权限。如为误操作，请移除机器人后重新添加！'
            await context.bot.send_message(
                chat_id=uid,
                text=message
            )

    async def _check_permissions(self, channel_id: int) -> bool:
        """检查机器人所在频道权限
        """
        chat_member = await self._application.bot.get_chat_member(chat_id=channel_id, user_id=self._application.bot.id)
        if chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            if not chat_member.can_manage_chat:
                return False
            elif not chat_member.can_post_messages:
                return False
            elif not chat_member.can_edit_messages:
                return False
            elif not chat_member.can_delete_messages:
                return False
            elif not chat_member.can_invite_users:
                return False
        else:
            return False

        return True
