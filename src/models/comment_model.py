from dataclasses import dataclass
import logging
from .media_model import MediaModel

logger = logging.getLogger(__name__)


@dataclass
class CommentLoaderModel:
    message: str
    media: MediaModel

    def __init__(self, message: str, media: MediaModel):
        self.message = message
        self.media = media
