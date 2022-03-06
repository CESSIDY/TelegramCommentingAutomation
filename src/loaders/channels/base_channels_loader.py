from abc import ABC, abstractmethod


class BaseChannelsLoader(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_all(self):
        pass
