from abc import ABC, abstractmethod
from typing import List
from .comment_model import CommentLoaderModel
from utils import images_dir, video_dir, documents_dir


class BaseCommentsLoader(ABC):
    _comments_list: List[CommentLoaderModel]
    base_images_dir = images_dir
    base_documents_dir = video_dir
    base_video_dir = documents_dir

    @abstractmethod
    def get_all(self) -> List[CommentLoaderModel]:
        pass
