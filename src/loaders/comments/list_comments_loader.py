from . import BaseCommentsLoader
from models import CommentLoaderModel, FileTypes, MediaModel
from typing import List


class ListCommentsLoader(BaseCommentsLoader):
    def __init__(self):
        super(ListCommentsLoader, self).__init__()

    def _parse_all_comments(self) -> List[CommentLoaderModel]:
        media = MediaModel(file_path=self._image_path("image_2.png"), file_type=FileTypes.IMAGE)
        self._comments_list = [CommentLoaderModel(message="Test comment #1", media=media)]
        return [CommentLoaderModel(message="Test comment #1", media=media)]
