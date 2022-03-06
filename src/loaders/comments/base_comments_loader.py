from abc import ABC, abstractmethod


class BaseCommentsLoader(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_all(self):
        pass
