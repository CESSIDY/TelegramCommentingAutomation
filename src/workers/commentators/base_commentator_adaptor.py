from loaders.channels import BaseChannelsLoader
from managers import ChannelsManager, SenderManager, MessagesManager, MediaManager
import logging
from models import CommentLoaderModel
from loaders.comments import BaseCommentsLoader
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCommentatorAdaptor(ABC):
    def __init__(self, client, comments_loader_adaptor: BaseCommentsLoader):
        self.comments_loader = comments_loader_adaptor
        self.client = client
        self.sender_manager = SenderManager(client=self.client, comments_loader=self.comments_loader)
        self.messages_manager = MessagesManager(client=self.client)
        self.media_manager = MediaManager(self.client)

    @abstractmethod
    async def commenting(self, channel, comment) -> bool:
        pass

    async def send_comment_to_post(self, channel, comment: CommentLoaderModel, post_id):
        media = None

        if comment.media:
            media = await self.media_manager.get_media_object(comment.media)

        result = await self.sender_manager.try_send_comment_with_retry(peer=channel,
                                                                       media=media,
                                                                       message=comment.message,
                                                                       reply_to_msg_id=post_id)
        return result
