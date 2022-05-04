from telethon.tl import functions, types
from telethon import tl
import logging

logger = logging.getLogger(__name__)


class MessagesManager:
    DISCUSSION_MESSAGES_LIMIT = 1000  # Limit for getting messages from discussion chat for some post

    def __init__(self, client):
        self.client = client
        self.user_owner = self.client.get_me()

    async def is_not_commented_post(self, discussion_channel, msg_id):
        discussion_messages = await self.get_last_messages_for_discussion(discussion_channel, msg_id)

        for message in discussion_messages:
            if self.user_owner.id == message.get('from_id', {}).get('user_id', None):
                return False
        return True

    async def get_last_messages_for_discussion(self, discussion_channel, msg_id) -> list:
        """
        Get comments for particular message (post) by ID

        :returns tl.types.messages.Messages: Instance of either Messages, MessagesSlice, ChannelMessages, MessagesNotModified.
        """
        all_messages = await self.get_last_messages(channel=discussion_channel, limit=self.DISCUSSION_MESSAGES_LIMIT)
        discussion_messages = list()
        for message in all_messages:
            if message['reply_to'] and message.get('reply_to', {}).get('reply_to_msg_id', None) == msg_id:
                discussion_messages.append(message)
        return discussion_messages

    async def get_last_messages(self, channel, limit=10) -> list:
        """
        :returns tl.types.messages.Messages: Instance of either Messages, MessagesSlice, ChannelMessages, MessagesNotModified.
        """
        offset_msg = 0
        all_messages = []
        limit_per_request = limit

        while True:
            try:
                history = await self.client(functions.messages.GetHistoryRequest(
                    peer=channel,
                    offset_id=offset_msg,
                    offset_date=None, add_offset=0,
                    limit=limit_per_request,
                    max_id=0,
                    min_id=0,
                    hash=0))
            except Exception as e:
                logger.error(e)
                return all_messages

            messages = history.messages
            if not messages:
                break

            for message in messages:
                all_messages.append(message.to_dict())

            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)

            if limit and total_messages >= limit:
                break

        return all_messages

    async def get_discussion_message(self, channel_id, message_id) -> tl.types.messages.DiscussionMessage or None:
        """
        If channel have discussion chat some messages gonna have they room in this chat,
        so we cat get discussion object for this message(post)
        """
        try:
            discussion_msg = await self.client(
                functions.messages.GetDiscussionMessageRequest(peer=channel_id,
                                                               msg_id=message_id))
            return discussion_msg
        except Exception as e:
            logger.warning(e)
        return
