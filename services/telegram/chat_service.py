from telegram.ext import Application

from db.daos.channel_dao import ChannelDao

class ChatService:
    def __init__(self, application: Application):
        self._application = application

    async def check_chat(self):
        channels = ChannelDao.get_all_validate_channels()
        for item in channels:
            # 是否已存在消息
            if self._is_exists_chat(item.id):
                self._update_chat(item.id)
            else:
                self._publish_chat(item.id)
    
    async def _is_exists_chat(self,channel_id:int) -> bool:
        pass

    async def _update_chat(self,channel_id:int) -> bool:
        pass

    async def _publish_chat(slf,channel_id:int) -> bool:
        pass


