from . import BaseCommentsLoader
from .comment_model import CommentLoaderModel


class JsonCommentsLoader(BaseCommentsLoader):
    def __init__(self):
        self._comments_list = [CommentLoaderModel(message="comment #1", videos=[], images=[]),
                               CommentLoaderModel(message="comment #2", videos=[], images=[])]

    def get_all(self) -> list:
        return self._comments_list
