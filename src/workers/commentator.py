from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader, CommentsChoosingMode
from managers import ChannelsManager, SenderManager, MessagesManager, MediaManager
import logging
from .base_worker import BaseWorker
from models import MediaModel, FileTypes, CommentLoaderModel
from loaders.comments import BaseCommentsLoader

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
        self.sender_manager = SenderManager(client=self.client, comments_loader=self.comments_loader)
        self.messages_manager = MessagesManager(client=self.client)
        self.media_manager = MediaManager(self.client)

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

        posts = await self.messages_manager.get_last_messages(channel=channel, limit=self.POSTS_LIMIT)

        if not posts:
            logger.warning(f"Empty posts list in channel({channel.title}/{channel.id})")
            return False

        for post in posts:
            result = await self.commenting_post(channel=channel, comment=comment, post_id=post["id"])
            if result:
                return True
        logger.warning(f"Could not leave comment under any message in channel({channel.title}/{channel.id})!")
        return False

    async def commenting_post(self, channel, comment: CommentLoaderModel, post_id) -> bool:
        # Getting discussion message object by id
        discussion_msg_object = await self.messages_manager.get_discussion_message(channel_id=channel.id,
                                                                                   message_id=post_id)

        if not discussion_msg_object:
            logger.warning(f"Could not get discussion messages from message({post_id})")
            return False

        # because can be more than 1 chat or message but first [0] its always main one
        discussion_channel_id = discussion_msg_object.chats[0].id
        discussion_msg_id = discussion_msg_object.messages[0].id

        discussion_channel = await self.channels_manager.get_chat_obj(discussion_channel_id)

        # check if we are not commented this post yet
        if await self.messages_manager.is_not_commented_post(discussion_channel, discussion_msg_id):
            commenting_result = await self.send_comment_to_post(channel=discussion_channel,
                                                                comment=comment,
                                                                post_id=discussion_msg_id)
            if not commenting_result:
                logger.warning(
                    f"Could not leave a comment message({discussion_msg_id}) in channel({channel.title}/{channel.id})")
                return False
            logger.info(f"Successfully added comment to channel({channel.title}/{channel.id})!")
            return True
        return False

    async def send_comment_to_post(self, channel, comment: CommentLoaderModel, post_id):
        media = None

        if comment.media:
            media = await self.media_manager.get_media_object(comment.media)

        result = await self.sender_manager.try_send_comment_with_retry(peer=channel,
                                                                       media=media,
                                                                       message=comment.message,
                                                                       reply_to_msg_id=post_id)
        return result
