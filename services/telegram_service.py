import asyncio

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler
from telegram.constants import ChatMemberStatus
import inject


from services.config_parser import ConfigParser
from db.daos.user_dao import UserDao
from db.daos.channel_dao import ChannelDao


class TelegramService:
    @inject.autoparams()
    def __init__(self, config_parser: ConfigParser):
        self._token = config_parser.get_bot_token()
        self._application = ApplicationBuilder().token(self._token).build()

        self._application.add_handler(CallbackQueryHandler(self._button_callback))
        self._application.add_handler(CommandHandler('start', self._start_command))
        self._application.add_handler(CommandHandler('help', self._help_command))
        self._application.add_handler(MessageHandler(filters.ALL, self._handle_message))
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

        keyboard = [
            [InlineKeyboardButton("🔥 添加机器人到频道", url=f'{self._application.bot.link}?startchannel&admin=post_messages+edit_messages+delete_messages+invite_users'),
             InlineKeyboardButton("🫰 管理我的频道", callback_data="manage_channel")],
            [InlineKeyboardButton("🚛 查看车队信息", callback_data="view_fleets")],
            [InlineKeyboardButton("📜 查看运行规则", callback_data="view_rules")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("请选择一个按钮：", reply_markup=reply_markup)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('无法识别的消息，请重新操作')

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()  # 响应按钮点击
        await query.edit_message_text(text=f"你点击了按钮 {query.data}")

    async def _track_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_member: ChatMemberUpdated = update.my_chat_member
        status = chat_member.new_chat_member.status
        uid = chat_member.from_user.id
        channel_id = chat_member.chat.id
        channel_name = chat_member.chat.username
        channel_title = chat_member.chat.title

        if status == ChatMemberStatus.ADMINISTRATOR:
            ChannelDao.add_channel(uid, channel_id, channel_name, channel_title)
            # await context.bot.send_message(
            #     chat_id=chat.id,
            #     text=f"{user.first_name} ({user.id}) added the bot to the channel {chat.title} ({chat.id})"
            # )
        elif status == ChatMemberStatus.LEFT or status == ChatMemberStatus.BANNED or ChatMemberStatus.RESTRICTED:
            # await context.bot.send_message(
            #     chat_id=chat.id,
            #     text=f"{user.first_name} ({user.id}) removed the bot from the channel {chat.title} ({chat.id})"
            # )
            ChannelDao.remove_channel(channel_id)
