from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class ButtonEnum(Enum):
    MANAGE_CHANNEL = 'manage_channel'
    VIEW_FLEETS = 'view_fleets'
    HOMEPAGE = 'homepage'


class BaseButtonStrategy(ABC):

    def __init__(self, tag: str) -> None:
        self.tag = tag

    @abstractmethod
    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        pass

    @abstractmethod
    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup], str]:
        pass


    def get_home_button(self) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton('🏡 返回首页', callback_data=ButtonEnum.HOMEPAGE.value)]
    
    def get_preview_button(self) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton('👈 返回上一页',callback_data=self.tag),
                InlineKeyboardButton('🏡 返回首页', callback_data=ButtonEnum.HOMEPAGE.value)]