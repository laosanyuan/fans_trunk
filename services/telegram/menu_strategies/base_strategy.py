from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from telegram import InlineKeyboardMarkup


class ButtonEnum(Enum):
    MANAGE_CHANNEL = 'manage_channel'
    VIEW_FLEETS = 'view_fleets'
    VIEW_RULES = 'view_rules'
    HOMEPAGE = 'homepage'


class BaseButtonStrategy(ABC):

    def __init__(self, tag: str) -> None:
        self.tag = tag

    @abstractmethod
    async def get_message_and_buttons(self, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        pass

    @abstractmethod
    async def handle_operation(self, sub_target: str, uid: int) -> Union[tuple[str, InlineKeyboardMarkup],str]:
        pass
