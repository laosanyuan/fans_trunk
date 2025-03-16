from datetime import datetime

from telegram.ext import Application, ExtBot


class ScoreService:

    def __init__(self, application: Application) -> None:
        self._bot: ExtBot = application.bot

    async def get_score_and_member(self, channel_id: int) -> tuple[int, int]:
        # 获取分数和成员数量
        member_count = await self._bot.get_chat_member_count(channel_id)
        score = self._get_score(member_count)
        # 根据管理员数量，目前数据不准
        admins = await self._bot.get_chat_administrators(channel_id)
        score -= (len(admins)-5)

        return max(0, int(score)), member_count

    def _get_score(self, member_count: int) -> int:
        base_core = 0
        if member_count < 100:
            base_core = 10 * member_count/100.0
        elif member_count < 500:
            base_core = 10 + 20 * (member_count-100)/400.0
        elif member_count < 1000:
            base_core = 30 + 10 * (member_count-500)/500.0
        elif member_count < 3000:
            base_core = 40 + 20 * (member_count-1000)/2000.0
        elif member_count < 5000:
            base_core = 60 + 10 * (member_count - 3000)/2000.0
        elif member_count < 10000:
            base_core = 70 + 10 * (member_count-5000)/5000.0
        elif member_count < 30000:
            base_core = 80 + 20 * (member_count-10000)/20000.0
        else:
            base_core = 100

        return base_core
