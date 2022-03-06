from abc import ABC, abstractmethod
from typing import List
from .channel_model import ChannelLoaderModel


class BaseChannelsLoader(ABC):
    _channels_ids_list: List[ChannelLoaderModel]

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_all(self) -> List[ChannelLoaderModel]:
        pass
