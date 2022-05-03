from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader, CommentsChoosingMode
from models import CommentLoaderModel
from managers import ChannelsManager
import logging
from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class Commentator(BaseWorker):
    POSTS_LIMIT = 10  # Limit the number of messages (posts) from channel we will review
    COMMENT_CHOOSING_MODE = CommentsChoosingMode.RANDOM  # Mode for selecting one comment from all

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

            _ = await self.commenting_last_uncommenting_posts(channel)

    async def commenting_last_uncommenting_posts(self, channel) -> bool:
        comment = self.comments_loader.get_comment_by_mode(mode=self.COMMENT_CHOOSING_MODE)

        posts = await self.channels_manager.get_last_messages(channel=channel, limit=self.POSTS_LIMIT)

        if not posts:
            logger.warning(f"Empty posts list in channel({channel.title}/{channel.id})")
            return False

        for post in posts:
            result = await self.send_comment_to_post(channel=channel, comment=comment, post=post)
            if result:
                return True
        logger.warning(f"Could not leave comment under any message in channel({channel.title}/{channel.id})!")
        return False

    async def send_comment_to_post(self, channel, comment: CommentLoaderModel, post) -> bool:
        # Getting discussion message object by id
        discussion_msg_object = await self.channels_manager.get_discussion_message(channel_id=channel.id,
                                                                                   message_id=post["id"])

        if not discussion_msg_object:
            logger.warning(f"Could not get discussion messages from message({post['id']})")
            return False

        # Get comments chat to this message (post)
        # discussion_msg_object.chats[0] = in chats we have 1-2 objects,
        # and the first is always the main chat that we are looking for
        discussion_channel = await self.channels_manager.get_chat_obj(discussion_msg_object.chats[0].id)

        # check if we are not commented this post yet
        if await self.channels_manager.is_not_commented_post(discussion_channel, discussion_msg_object.messages[0].id):
            commenting_result = await self.channels_manager.commenting_post(channel=discussion_channel,
                                                                            comment=comment,
                                                                            comments_loader=self.comments_loader,
                                                                            post_id=discussion_msg_object.messages[
                                                                                0].id)
            if not commenting_result:
                logger.warning(
                    f"Could not leave a comment message({discussion_msg_object.messages[0].id}) in channel({channel.title}/{channel.id})")
                return False
            logger.info(f"Successfully added comment to channel({channel.title}/{channel.id})!")
            return True
        return False
