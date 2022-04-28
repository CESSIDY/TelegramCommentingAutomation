from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader, CommentLoaderModel, FileTypes
from managers import ChannelsManager
from typing import List
import logging
import random
from enum import Enum

logger = logging.getLogger(__name__)


class CommentsChoosingMode(Enum):
    RANDOM = 1
    TEXT_PREFER = 2
    VIDEO_PREFER = 3
    IMAGE_PREFER = 4


class Commentator:
    POST_MESSAGES_LIMIT = 10
    COMMENT_CHOOSING_MODE = CommentsChoosingMode.RANDOM

    def __init__(self, client, comments_loader_adaptor: BaseCommentsLoader,
                 channels_loader_adaptor: BaseChannelsLoader):
        self.comments_loader = comments_loader_adaptor
        self.channels_loader = channels_loader_adaptor
        self.client = client
        self.channels_manager = ChannelsManager(client=self.client, channels_loader_adaptor=self.channels_loader)
        self.comments: List[CommentLoaderModel] = self.comments_loader.get_all()

    def run_until_complete(self):
        with self.client:
            self.client.loop.run_until_complete(self.start_commenting())

    async def start_commenting(self):
        channels = await self.channels_manager.get_channels()
        for channel in await channels:
            logger.info(f"Try left comment to channel({channel.title}/{channel.id})")

            _ = await self.commenting_last_uncommenting_message(channel, limit=self.POST_MESSAGES_LIMIT)

    async def commenting_last_uncommenting_message(self, channel, limit):
        comment = await self._get_comments(self.comments, self.COMMENT_CHOOSING_MODE)

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

    async def send_comment_to_post(self, channel, comment, post_message):
        discussion_msg = await self.channels_manager.get_discussion_message(channel=channel, message=post_message)

        if not discussion_msg:
            logger.error(f"Could not get discussion messages from message({post_message['id']})")
            return False

        discussion_channel = await self.channels_manager.get_chat_obj(discussion_msg.chats[0].id)

        if await self.channels_manager.is_not_commenting_post(discussion_channel, discussion_msg.messages[0].id):
            commenting_result = await self.channels_manager.commenting_message(channel=discussion_channel,
                                                                               comment=comment,
                                                                               comments=self.comments,
                                                                               message_id=discussion_msg.messages[
                                                                                   0].id)
            if not commenting_result:
                logger.warning(
                    f"Could not leave a comment message({discussion_msg.messages[0].id}) in channel({channel.title}/{channel.id})")
                return False
            logger.info(f"Successfully added comment to channel({channel.title}/{channel.id})!")
            return True
        return False

    @staticmethod
    async def _get_comments(comments: List[CommentLoaderModel], choosing_flag: CommentsChoosingMode):
        if comments:
            comment_result = comments[0]
            if choosing_flag == CommentsChoosingMode.RANDOM:
                comment_result = random.choices(comments)[0]
            elif choosing_flag == CommentsChoosingMode.TEXT_PREFER:
                for comment in comments:
                    if not comment.file_path and comment.message:
                        comment_result = comment
                        break
            elif choosing_flag == CommentsChoosingMode.IMAGE_PREFER:
                for comment in comments:
                    if comment.file_path == FileTypes.IMAGE:
                        comment_result = comment
                        break
            elif choosing_flag == CommentsChoosingMode.VIDEO_PREFER:
                for comment in comments:
                    if comment.file_path == FileTypes.VIDEO:
                        comment_result = comment
                        break
            return comment_result
        logger.error("List of comments is empty")
        return None
