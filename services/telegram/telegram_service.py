import asyncio


from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler
from telegram.constants import ChatMemberStatus
import inject


from services.config_parser import ConfigParser
from services.score_service import ScoreService
from services.telegram.menu_strategy_manager import MenuStrategyManager, ButtonEnum
from db.daos.user_dao import UserDao
from db.daos.channel_dao import ChannelDao
from db.daos.fleet_dao import FleetDao


class TelegramService:
    @inject.autoparams()
    def __init__(self, config_parser: ConfigParser, score_service: ScoreService):
        self._score_service = score_service
        self._token = config_parser.get_bot_token()
        self._menu_strategy_manager = MenuStrategyManager()

        self._application = ApplicationBuilder().token(self._token).build()
        self._application.add_handler(CallbackQueryHandler(self._button_callback))
        self._application.add_handler(CommandHandler('start', self._start_command))
        self._application.add_handler(CommandHandler('help', self._help_command))
        self._application.add_handler(ChatMemberHandler(self._track_chat_member, ChatMemberHandler.ANY_CHAT_MEMBER))

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._application.run_polling(close_loop=False)

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        user_name = update.effective_user.username
        full_name = update.effective_user.full_name
        UserDao.add_user(uid=uid, user_name=user_name, full_name=full_name)

        self._application.bot
        strategy = self._menu_strategy_manager.get_strategy(ButtonEnum.HOMEPAGE.value, self._application.bot)
        message, reply_markup = strategy.get_message_and_buttons(uid)

        await update.message.reply_text(message, reply_markup=reply_markup)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        callback_data = query.data
        uid = query.from_user.id
        strategy = self._menu_strategy_manager.get_strategy(callback_data, self._application.bot)
        message, button = strategy.get_message_and_buttons(uid)

        await query.answer()
        await query.edit_message_text(text=message, reply_markup=button)

    async def _track_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 处理添加移除机器人
        chat_member: ChatMemberUpdated = update.my_chat_member
        status = chat_member.new_chat_member.status
        uid = chat_member.from_user.id
        channel_id = chat_member.chat.id
        channel_name = chat_member.chat.username
        channel_title = chat_member.chat.title

        if status == ChatMemberStatus.ADMINISTRATOR:
            fans_count = await self._application.bot.get_chat_member_count(channel_id)
            # 暂未实现获取浏览量
            view_count = 0.05*fans_count
            score = self._score_service.get_score(fans_count, view_count)
            fleet = FleetDao.get_fleet(score)
            ChannelDao.add_channel(uid, channel_id, channel_name, channel_title, fleet.id)

            message = f'''恭喜您，添加频道成功！

系统根据您的频道数据智能评级，【{channel_title}】当前的得分为【{score}】，分配于{fleet.name}！

注意，当前的评分和分配车队都是基于此频道目前的数据计算得出，随着数据的变化，评分和分配车队随时也会随时发生变化。

✈ 马上发车！'''

            await context.bot.send_message(
                chat_id=uid,
                text=message
            )
        elif status == ChatMemberStatus.LEFT or status == ChatMemberStatus.BANNED or ChatMemberStatus.RESTRICTED:
            ChannelDao.remove_channel(channel_id)

            message = f'您的频道【{channel_title}】已失去权限。如为误操作，请移除机器人后重新添加！'
            await context.bot.send_message(
                chat_id=uid,
                text=message
            )
