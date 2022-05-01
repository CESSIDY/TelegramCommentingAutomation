from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader, CommentsChoosingMode
from managers import ChannelsManager
import logging
from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class Commentator(BaseWorker):
    POST_MESSAGES_LIMIT = 10
    COMMENT_CHOOSING_MODE = CommentsChoosingMode.RANDOM

    def __init__(self, client, comments_loader_adaptor: BaseCommentsLoader,
                 channels_loader_adaptor: BaseChannelsLoader):
        self.comments_loader = comments_loader_adaptor
        self.channels_loader = channels_loader_adaptor
        self.client = client
        self.channels_manager = ChannelsManager(client=self.client, channels_loader_adaptor=self.channels_loader)

    def run_until_complete(self):
        with self.client:
            self.client.loop.run_until_complete(self.start_commenting())

    async def start_commenting(self):
        channels = await self.channels_manager.get_channels()
        for channel in await channels:
            logger.info(f"Try left comment to channel({channel.title}/{channel.id})")

            _ = await self.commenting_last_uncommenting_message(channel, limit=self.POST_MESSAGES_LIMIT)

    async def commenting_last_uncommenting_message(self, channel, limit) -> bool:
        comment = self.comments_loader.get_comment_by_mode(mode=self.COMMENT_CHOOSING_MODE)

        post_messages = await self.channels_manager.get_last_messages(channel=channel, limit=limit)

        if not post_messages:
            logger.warning(f"Empty posts list in channel({channel.title}/{channel.id})")
            return False

        for post_message in post_messages:
            result = await self.send_comment_to_post(channel=channel, comment=comment, post_message=post_message)
            if result:
                return True
        logger.warning(f"Could not leave comment under any message in channel({channel.title}/{channel.id})!")
        return False

    async def send_comment_to_post(self, channel, comment, post_message) -> bool:
        discussion_msg = await self.channels_manager.get_discussion_message(channel=channel, message=post_message)

        if not discussion_msg:
            logger.error(f"Could not get discussion messages from message({post_message['id']})")
            return False

        discussion_channel = await self.channels_manager.get_chat_obj(discussion_msg.chats[0].id)

        if await self.channels_manager.is_not_commenting_post(discussion_channel, discussion_msg.messages[0].id):
            commenting_result = await self.channels_manager.commenting_post(channel=discussion_channel,
                                                                            comment=comment,
                                                                            comments_loader=self.comments_loader,
                                                                            post_id=discussion_msg.messages[0].id)
            if not commenting_result:
                logger.warning(
                    f"Could not leave a comment message({discussion_msg.messages[0].id}) in channel({channel.title}/{channel.id})")
                return False
            logger.info(f"Successfully added comment to channel({channel.title}/{channel.id})!")
            return True
        return False
