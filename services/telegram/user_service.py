import asyncio

from telegram import Update, ChatMemberUpdated
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, ChatMemberHandler, Application
from telegram.constants import ChatMemberStatus, ParseMode
import inject

from services.channel_data_provider import ChannelDataProvider
from services.telegram.menu_strategies.menu_strategy_manager import MenuStrategyManager, ButtonEnum
from services.telegram.score_service import ScoreService
from db.daos.user_dao import UserDao
from db.daos.channel_dao import ChannelDao
from db.daos.fleet_dao import FleetDao


class UserService:
    def __init__(self, application: Application):
        self._application = application
        self._menu_strategy_manager = MenuStrategyManager(self._application.bot)
        self._score_service = ScoreService(application)
        self._channel_data_provider = inject.instance(ChannelDataProvider)

        self._application.add_handler(CallbackQueryHandler(self._button_callback))
        self._application.add_handler(CommandHandler('start', self._start_command))
        self._application.add_handler(CommandHandler('help', self._help_command))
        self._application.add_handler(ChatMemberHandler(self._track_chat_member, ChatMemberHandler.ANY_CHAT_MEMBER))

    async def update_all_user_data(self):
        """更新全部用户车队数据
        """
        channels = ChannelDao.get_all_validate_channels()
        for channel in channels:
            score, member_count = await self._score_service.get_score_and_member(channel.id)
            if score == 0 and member_count == 0:
                continue

            fleet = FleetDao.get_fleet_by_score(score)
            ChannelDao.update_member_count(channel.id, member_count, fleet.id)

            if fleet.id != channel.fleet_id:
                # 车队数据发生变更时通知用户
                before_fleet = FleetDao.get_fleet_by_id(channel.fleet_id)
                message = ''
                if score >= before_fleet.max_score:
                    message = f'🎉 恭喜，您的频道【{channel.title}】由于数据良好，系统评级得到提升，当前分数为{score}！\n现将您的车队从原来的<b>{before_fleet.name}</b>升级到<b>{fleet.name}</b>！！！\n\n请您再接再励，车队等级提升将会为您带来更优质的曝光和流量！！'
                else:
                    message = f'💔 很遗憾，由于您的频道【{channel.title}】质量下降，系统已更新您频道的评级，当前分数为{score}！\n现将您的频道从<b>{before_fleet.name}</b>降级到<b>{fleet.name}</b>！！！\n\n为了提升您的推广效果，请注意您的频道运营数据，优质的频道数据和评级将会得到系统更多和更优质的曝光效果！'
                await self._application.bot.send_message(
                    chat_id=channel.user_id,
                    text=message,
                    parse_mode=ParseMode.HTML)

            await asyncio.sleep(1)

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        user_name = update.effective_user.username
        full_name = update.effective_user.full_name
        UserDao.add_user(uid=uid, user_name=user_name, full_name=full_name)

        message, reply_markup = await self._menu_strategy_manager.get_message_and_buttons(ButtonEnum.HOMEPAGE.value, uid)
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = f'''
✨ 欢迎使用【{self._application.bot.first_name}】——您的频道增长智能管家！
🔥 精准流量匹配 | 公平透明机制 | 7×24小时护航

🚀 核心功能
✅ 全自动智能评级发车
- 无需手动操作，系统实时监测数据，根据综合评级自动匹配最佳车队
- 告别低效车队，算法动态优化曝光权重，低分车队将被限制推广
✅ 评级维度
- 成员数量和活跃度
- 内容质量、发布频率、阅读量、交互率
- 互推车使用时长
- 违规内容、敏感操作、刷粉等会导致扣分

🔄 互推规则
- 每小时发车 | 随机乱序排列
- 更大流量池，区别于传统互推车选车模式，我们采用大型车队发车
- 历史广告自动清理，避免信息过载
- 每日自动同步粉丝数据，智能匹配新车队

🌟 示例说明：
假设您的某个频道被系统评级后分配到【黄金车队】，此时黄金车队中包含200个频道，合集成员数量300000人。
1️⃣ 随机抓取
- 每小时从200个频道库中动态抽取X个频道（X=10~20随机值）
- 采用量子随机算法保证公平性
2️⃣ 乱序轮播
- 每次推送自动打乱频道排列顺序
- 避免头部效应，确保平等曝光机会
3️⃣ 累积覆盖
- 72小时内 100%触达全部200个频道的300000人
- 您的频道将同步出现在其他199个成员的推送列表

⚠️ 违规高压线（触犯立即永久封禁）
❗<b>诈骗/未成年相关/暴力/政治/军火/重口内容</b>

🛡️ 郑重声明
{self._application.bot.first_name}为完全免费项目，谨防付费诈骗！
助力真实流量增长，我们永不收费！

点击 /start 命令开始使用
'''
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

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
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

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
                score, member_count = await self._score_service.get_score_and_member(channel_id)
                if score == 0 and member_count == 0:
                    message = f'🚫 频道【{channel_title}】由于数据异常，无法进行发车，请重新添加！'
                    await context.bot.send_message(
                        chat_id=uid,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                    return
                fleet = FleetDao.get_fleet_by_score(score)
                fake_channels, fake_members = self._channel_data_provider.get_fleet_summary(fleet.id)

                ChannelDao.add_channel(uid, channel_id, channel_name, channel_title, fleet.id, has_permission, score, member_count)
                FleetDao.update_fleets_data()

                if has_permission:
                    message = f'''🎉 恭喜您，添加频道成功！

系统根据您的频道数据智能评级，【<b>{channel_title}</b>】当前的得分为<b>{score}</b>，分配于<b>{fleet.name}</b>，本车队包含频道数量：<b>{fake_channels + 1}</b>，合计覆盖成员数量：<b>{fake_members}</b>！

注意，当前的评分和分配车队都是基于此频道目前的数据计算得出，随着数据的变化，评分和分配车队随时也会随时发生变化。

✈ 祝大哥发财，马上发车！'''
                else:
                    message = f'🚫 频道【{channel_title}】添加成功，但当前缺少运行权限无法运行，请赋予必要权限或删除后重新添加。\n\n机器人需要获得必要操作权限，然后才能发车！'

            await context.bot.send_message(
                chat_id=uid,
                text=message,
                parse_mode=ParseMode.HTML
            )
        elif status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED):
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
