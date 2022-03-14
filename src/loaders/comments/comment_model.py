from dataclasses import dataclass
from enum import Enum
from os.path import exists
import logging

logger = logging.getLogger(__name__)


class FileTypes(Enum):
    VIDEO = 1
    TEXT_DOCUMENT = 2  # txt, csv, doc...
    APPLICATION_DOCUMENT = 3  # zip, pdf...
    IMAGE = 4


@dataclass
class CommentLoaderModel:
    message: str
    file_path: [str, None]
    file_type: [FileTypes, None]

    def __init__(self, message: str, file_path: [str, None], file_type: [FileTypes, None]):
        self.message = message
        self.file_path = self._check_if_file_exists(file_path)
        self.file_type = file_type

    @staticmethod
    def _check_if_file_exists(file_path):
        if exists(file_path):
            return file_path
        logger.warning(f"File does not exist: {file_path}")
        return None
