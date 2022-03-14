from abc import ABC, abstractmethod
from typing import List
from .comment_model import CommentLoaderModel


class BaseCommentsLoader(ABC):
    _comments_list: List[CommentLoaderModel]

    def __init__(self, config):
        self.base_images_dir = config['Files']['base_images_dir']
        self.base_documents_dir = config['Files']['base_documents_dir']
        self.base_video_dir = config['Files']['base_video_dir']

    @abstractmethod
    def get_all(self) -> List[CommentLoaderModel]:
        pass
