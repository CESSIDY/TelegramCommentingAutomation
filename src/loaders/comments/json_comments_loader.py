from . import BaseCommentsLoader
from .comment_model import CommentLoaderModel, FileTypes


class JsonCommentsLoader(BaseCommentsLoader):
    base_images_dir = "C:\\Users\\vrupa\\PycharmProjects\\BWT\\Telegram_Parsing\\Scraper\\TelegramCommentingAutomation\\media\\images"
    base_documents_dir = "C:\\Users\\vrupa\\PycharmProjects\\BWT\\Telegram_Parsing\\Scraper\\TelegramCommentingAutomation\\media\\documents"
    base_video_dir = "C:\\Users\\vrupa\\PycharmProjects\\BWT\\Telegram_Parsing\\Scraper\\TelegramCommentingAutomation\\media\\video"

    def __init__(self):
        self._comments_list = [
                               CommentLoaderModel(message="comment #2",
                                                  file_path=f"{self.base_video_dir}\\video_1.mp4",
                                                  file_type=FileTypes.VIDEO)
                               ]

    def get_all(self) -> list:
        return self._comments_list
