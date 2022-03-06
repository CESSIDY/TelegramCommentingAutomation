from abc import ABC, abstractmethod
from typing import List
from .comment_model import CommentLoaderModel


class BaseCommentsLoader(ABC):
    _comments_list: List[CommentLoaderModel]

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_all(self) -> List[CommentLoaderModel]:
        pass
