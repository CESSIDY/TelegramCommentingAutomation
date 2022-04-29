from abc import ABC, abstractmethod
from typing import List
from utils import images_dir, video_dir, documents_dir
import random
import logging
from models import MediaModel, FileTypes, CommentLoaderModel

logger = logging.getLogger(__name__)


class BaseCommentsLoader(ABC):
    _comments_list: List[CommentLoaderModel]
    base_images_dir = images_dir
    base_documents_dir = documents_dir
    base_video_dir = video_dir

    def __init__(self):
        self._comments_list = self._parse_all_comments()

    def get_all(self) -> List[CommentLoaderModel]:
        return self._comments_list

    @abstractmethod
    def _parse_all_comments(self) -> List[CommentLoaderModel]:
        pass

    def get_first_comment(self) -> (CommentLoaderModel or None):
        if self._comments_list and len(self._comments_list):
            return self._comments_list[0]
        return

    def get_random_comment(self) -> (CommentLoaderModel or None):
        if self._comments_list:
            comment = random.choices(self._comments_list)
            if len(comment):
                return comment[0]
        return

    def get_text_comment(self) -> (CommentLoaderModel or None):
        for comment in self._comments_list:
            if not comment.media and comment.message:
                return comment
        return

    def get_image_comment(self) -> (CommentLoaderModel or None):
        for comment in self._comments_list:
            if comment.media and comment.media.file_path == FileTypes.IMAGE:
                return comment
        return

    def get_video_comment(self) -> (CommentLoaderModel or None):
        for comment in self._comments_list:
            if comment.media and comment.media.file_path == FileTypes.VIDEO:
                return comment
        return

    def _doc_path(self, file_name):
        return f"{self.base_documents_dir}\\{file_name}"

    def _image_path(self, file_name):
        return f"{self.base_images_dir}\\{file_name}"

    def _video_path(self, file_name):
        return f"{self.base_video_dir}\\{file_name}"

    def __getitem__(self, item):
        return self._comments_list[item]
