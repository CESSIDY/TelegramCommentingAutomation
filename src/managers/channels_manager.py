from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader
from telethon.tl import functions, types
from telethon import tl
from telethon.tl.types import ChatInviteAlready, ChatInvite
import logging
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.errors import InviteHashExpiredError
from .media_manager import MediaManager
from models import MediaModel, FileTypes, CommentLoaderModel

logger = logging.getLogger(__name__)


class ChannelsManager:
    DISCUSSION_MESSAGES_LIMIT = 1000  # Limit for getting messages from discussion chat for some post

    def __init__(self, client, channels_loader_adaptor: BaseChannelsLoader):
        self.channels_list = self._get_channels_objects(channels_loader_adaptor)
        self.client = client
        self.media_manager = MediaManager(self.client)
        self.user_owner = self.client.get_me()

    async def _get_channels_objects(self, channels_loader: BaseChannelsLoader) -> list:
        channels_list = list()

        for channel_info in channels_loader.get_all():
            if channel_info.private:
                channel = await self.get_private_channel(channel_info)
            else:
                channel = await self.get_public_channel(channel_info)

            if channel:
                channels_list.append(channel)

        return channels_list

    async def get_channels(self):
        return self.channels_list

    async def get_private_channel(self, channel_info):
        channel = None

        try:
            # Try get channel invite object by hash_id
            channel_invite = await self.client(CheckChatInviteRequest(channel_info.id))
            if channel_invite:
                if isinstance(channel_invite, ChatInvite):
                    # If channel_invite is not expired we can try join to the channel
                    channel_updates = await self.client(functions.messages.ImportChatInviteRequest(channel_info.id))
                    channel = channel_updates.chats[0]
                elif isinstance(channel_invite, ChatInviteAlready):
                    # Account already subscribe to the channel and we can just get channel object from channel_invite
                    channel = channel_invite.chat
                if channel:
                    channel = await self.get_chat_obj(channel.id)
                return channel
        except InviteHashExpiredError as err:
            pass

        # If invite hash expired than we can try just join to channels by request
        channels_updates = await self.client(functions.channels.JoinChannelRequest(
            channel=channel_info.id
        ))

        return channels_updates.chats[0]

    async def get_public_channel(self, channel_info):
        channel = await self.get_chat_obj(channel_info.id)
        return channel

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

    async def commenting_post(self, channel, comment: CommentLoaderModel, comments_loader: BaseCommentsLoader, post_id):
        media = None

        if comment.media:
            media = await self.media_manager.get_media_object(comment.media)

        result = await self._try_send_comment_with_retry(comments_loader=comments_loader,
                                                         peer=channel,
                                                         media=media,
                                                         message=comment.message,
                                                         reply_to_msg_id=post_id)
        return result

    async def _try_send_comment_with_retry(self, comments_loader, peer, message, reply_to_msg_id, media=None):
        if media:
            result = await self._send_media_comment(media=media,
                                                    peer=peer,
                                                    message=message,
                                                    reply_to_msg_id=reply_to_msg_id)
            if result:
                return result

            logger.info("Try re-send text message")
            comment = comments_loader.get_text_comment()
            if comment:
                message = comment.message

        return await self._send_text_comment(peer=peer,
                                             message=message,
                                             reply_to_msg_id=reply_to_msg_id)

    async def _send_media_comment(self, media, peer, message, reply_to_msg_id):
        try:
            result = await self.client(functions.messages.SendMediaRequest(peer=peer,
                                                                           media=media,
                                                                           message=message,
                                                                           reply_to_msg_id=reply_to_msg_id))
            return result
        except Exception as e:
            logger.warning(e)
        return

    async def _send_text_comment(self, peer, message, reply_to_msg_id):
        try:
            result = await self.client(functions.messages.SendMessageRequest(peer=peer,
                                                                             message=message,
                                                                             reply_to_msg_id=reply_to_msg_id))
            return result
        except Exception as e:
            logger.warning(e)
        return

    async def get_chat_obj(self, channel_id) -> tl.types.channels.ChannelParticipant or None:
        try:
            channel_obj = await self.client(functions.channels.GetChannelsRequest(
                id=[channel_id]
            ))
        except Exception as e:
            logger.info(e)
            return
        return channel_obj.chats[0]
