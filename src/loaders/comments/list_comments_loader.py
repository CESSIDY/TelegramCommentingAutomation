from . import BaseCommentsLoader
from .comment_model import CommentLoaderModel, FileTypes


class ListCommentsLoader(BaseCommentsLoader):
    def __init__(self):
        self._comments_list = [
                               CommentLoaderModel(message="Test comment #1",
                                                  file_path=self._image_path("image_2.png"),
                                                  file_type=FileTypes.IMAGE)
                               ]

    def _doc_path(self, file_name):
        return f"{self.base_documents_dir}\\{file_name}"

    def _image_path(self, file_name):
        return f"{self.base_images_dir}\\{file_name}"

    def _video_path(self, file_name):
        return f"{self.base_video_dir}\\{file_name}"

    def get_all(self) -> list:
        return self._comments_list
