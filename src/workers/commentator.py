from loaders.channels import BaseChannelsLoader
from loaders.comments import CommentsChoosingMode
from managers import ChannelsManager
import logging
from .base_worker import BaseWorker
from loaders.comments import BaseCommentsLoader
from .commentators import BaseCommentatorAdaptor

logger = logging.getLogger(__name__)


class Commentator(BaseWorker):
    COMMENT_CHOOSING_MODE = CommentsChoosingMode.RANDOM  # Mode for selecting one comment from all

    def __init__(self, client, comments_loader_adaptor: BaseCommentsLoader,
                 channels_loader_adaptor: BaseChannelsLoader, commenting_adaptor: BaseCommentatorAdaptor):
        self.comments_loader = comments_loader_adaptor
        self.channels_loader = channels_loader_adaptor
        self.commenting_adaptor = commenting_adaptor
        self.client = client
        self.channels_manager = ChannelsManager(client=self.client, channels_loader_adaptor=self.channels_loader)

    def run_until_complete(self):
        with self.client:
            self.client.loop.run_until_complete(self.start_commenting())

    async def start_commenting(self):
        channels = await self.channels_manager.get_channels()
        for channel in await channels:
            logger.info(f"Try left comment to channel({channel.title}/{channel.id})")

            comment = self.comments_loader.get_comment_by_mode(mode=self.COMMENT_CHOOSING_MODE)
            _ = await self.commenting_adaptor.commenting(channel=channel, comment=comment)
