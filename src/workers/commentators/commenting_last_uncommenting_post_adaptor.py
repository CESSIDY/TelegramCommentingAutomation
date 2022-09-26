import logging
from . import BaseCommentatorAdaptor

logger = logging.getLogger(__name__)


class CommentingLastUncommentingPostAdaptor(BaseCommentatorAdaptor):
    POSTS_LIMIT = 10  # Limit the number of messages (posts) from channel we will review

    async def commenting(self, channel, comment) -> bool:
        posts = await self.messages_manager.get_last_messages(channel=channel, limit=self.POSTS_LIMIT)

        for post in posts:
            # Getting discussion message object by id
            discussion_msg_object = await self.messages_manager.get_discussion_message(channel_id=channel.id,
                                                                                       message_id=post["id"])

            if not discussion_msg_object:
                logger.warning(f"Could not get discussion messages from message({post['id']})")
                continue

            # because can be more than 1 chat or message but first [0] its always main one
            discussion_msg_id = discussion_msg_object.messages[0].id
            discussion_channel = discussion_msg_object.chats[0]

            # check if we are not commented this post yet
            if not await self.messages_manager.is_commented_post(discussion_channel, discussion_msg_id):
                commenting_result = await self.send_comment_to_post(channel=discussion_channel,
                                                                    comment=comment,
                                                                    post_id=discussion_msg_id)
                if commenting_result:
                    logger.info(f"Successfully added comment to channel({channel.title}/{channel.id})!")
                    return True

        logger.warning(f"Could not leave comment under any post in channel({channel.title}/{channel.id})!")
        return False
