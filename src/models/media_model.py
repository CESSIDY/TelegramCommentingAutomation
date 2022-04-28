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
class MediaModel:
    file_path: [str, None]
    file_type: [FileTypes, None]

    def __init__(self, file_path: [str, None], file_type: [FileTypes, None]):
        self.file_path = self._check_if_file_exists(file_path)
        self.file_type = file_type

    @staticmethod
    def _check_if_file_exists(file_path):
        if file_path and exists(file_path):
            return file_path
        elif file_path:
            logger.warning(f"File does not exist: {file_path}")
        return None

    def get_file_name(self) -> str:
        if self.file_path:
            return self.file_path.split("\\")[-1]
        return ''

    def get_file_extension(self):
        if self.file_path and "." in self.file_path:
            return self.file_path.split(".")[-1]
        return ''

    def __bool__(self):
        return True if self.file_path and self.file_type else False
