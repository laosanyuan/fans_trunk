from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import inject

from services.telegram.menu_strategies.menu_strategy_manager import MenuStrategyManager
from services.config_parser import ConfigParser
from db.daos.fleet_dao import FleetDao
from db.daos.user_dao import UserDao
from db.daos.channel_dao import ChannelDao


class AdminService:
    def __init__(self, application: Application):
        self._admin_user = inject.instance(ConfigParser).get_admin_user()
        self._application = application
        self._menu_strategy_manager = MenuStrategyManager(self._application.bot)

        self._application.add_handler(CommandHandler('admin', self._admin_command))

    async def _admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_name = update.effective_user.username
        message = '未知命令！'

        if user_name == self._admin_user:
            users = UserDao.get_user_count()
            channels, memebers = FleetDao.get_channel_summary()

            message = f'用户数量：{users}\n频道数量：{channels}\n成员数量：{memebers}\n\n'
            message += '以下是成员数量前50的频道数据：\n'

            tmp_channels = ChannelDao.get_channels()
            for index, item in enumerate(tmp_channels):
                message += f'{index+1}. <b><a href="https://t.me/{item.name}">{item.title}</a></b> - {item.member_count}\n'

        await update.message.reply_text(
            message,
            parse_mode='HTML',
            write_timeout=60,
            connect_timeout=60,
            pool_timeout=60,
            read_timeout=60,
            disable_web_page_preview=True
        )
