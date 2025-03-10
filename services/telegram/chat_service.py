from telegram.ext import Application


class ChatService:
    def __init__(self, application: Application):
        self._application = application