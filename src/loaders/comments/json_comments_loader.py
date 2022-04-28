from . import BaseCommentsLoader
from models import CommentLoaderModel, FileTypes, MediaModel
import os
import json
import logging
from typing import List

logger = logging.getLogger(__name__)


class JsonCommentsLoader(BaseCommentsLoader):
    def __init__(self):
        self.base_comments_path = os.path.abspath(os.path.join(os.path.realpath(__file__),
                                                               "..", "..", "..", "..", "data", "comments"))
        self._comments_list = self._get_all_comments()

    def _get_all_comments(self) -> List[CommentLoaderModel]:
        json_files = self._get_all_json_comments_files()
        comments_list = self._get_comments_from_json_files(json_files)
        comments_models_list = self._convert_comments_list_to_comments_models(comments_list)

        logger.info(f"comments: {len(comments_models_list)}")
        return comments_models_list

    def _get_all_json_comments_files(self) -> list:
        json_files = []
        for pos_json in os.listdir(self.base_comments_path):
            if pos_json.endswith('.json'):
                json_files.append(os.path.join(self.base_comments_path, pos_json))

        return json_files

    @staticmethod
    def _get_comments_from_json_files(json_files: list) -> List[dict]:
        data_list = []
        for json_file in json_files:
            with open(json_file, mode="r", encoding="utf-8") as file:
                json_data = file.read()
                data = json.loads(json_data)
                data_list.extend(data)
        return data_list

    def _convert_comments_list_to_comments_models(self, comments_list: List[dict]) -> List[CommentLoaderModel]:
        comments_models_list = []

        for comment in comments_list:
            if comment.get("message"):
                file_type, file_path = self._load_file_data(comment)

                media = MediaModel(file_path=file_path, file_type=file_type)
                comment_model = CommentLoaderModel(message=comment["message"], media=media)

                comments_models_list.append(comment_model)
            else:
                logger.warning(f"Can't load comment obj: {comment}")
        return comments_models_list

    def _load_file_data(self, comment) -> (FileTypes, str):
        file_type = None
        file_path = None

        if not comment.get("file_name"):
            return file_type, file_path

        if comment.get("file_type") == "image":
            file_type = FileTypes.IMAGE
            file_path = self._image_path(comment["file_name"])
        elif comment.get("file_type") == "video":
            file_type = FileTypes.VIDEO
            file_path = self._video_path(comment["file_name"])
        elif comment.get("file_type") == "document":
            file_type = FileTypes.TEXT_DOCUMENT
            file_path = self._doc_path(comment["file_name"])
        elif comment.get("file_type") == "application":
            file_type = FileTypes.APPLICATION_DOCUMENT
            file_path = self._doc_path(comment["file_name"])
        else:
            logger.warning(f"Can't load file_type from obj: {comment} "
                           f"it needs to be one of those: ['image', 'video', 'document', 'application']")
        return file_type, file_path

    def _doc_path(self, file_name):
        return f"{self.base_documents_dir}\\{file_name}"

    def _image_path(self, file_name):
        return f"{self.base_images_dir}\\{file_name}"

    def _video_path(self, file_name):
        return f"{self.base_video_dir}\\{file_name}"

    def get_all(self) -> List[CommentLoaderModel]:
        return self._comments_list
