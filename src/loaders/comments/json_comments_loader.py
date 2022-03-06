from . import BaseCommentsLoader


class JsonCommentsLoader(BaseCommentsLoader):
    def __init__(self):
        self._comments_list = ["comment #666", "comment #999"]

    def get_all(self) -> list:
        return self._comments_list
