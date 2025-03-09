from abc import ABC, abstractmethod
from enum import Enum

class ButtonEnum(Enum):
    MANAGE_CHANNEL = 'manage_channel'
    VIEW_FLEETS = 'view_fleets'
    VIEW_RULES = 'view_rules'

    HOMEPAGE = 'homepage'

class BaseButtonStrategy(ABC):

    def __init__(self, tag: str) -> None:
        self.tag = tag

    @abstractmethod
    def get_message_and_buttons(self, uid: int) -> tuple[str, list]:
        pass

    @abstractmethod
    def handle_operation(self, sub_target: str) -> None:
        pass
