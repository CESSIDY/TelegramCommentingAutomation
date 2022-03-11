from loaders.channels import BaseChannelsLoader
from loaders.comments import CommentLoaderModel, FileTypes
from telethon.tl import functions, types
from telethon.tl.types import Updates, ChatInviteAlready, ChatInvite, InputFile, DocumentAttributeVideo, DocumentAttributeFilename
import logging
import random
from pprint import pprint
from telethon.tl.functions.messages import CheckChatInviteRequest

logger = logging.getLogger(__name__)


class ChannelsManager:
    MESSAGES_LIMIT = 100

    def __init__(self, client, channels_loader_adaptor: BaseChannelsLoader):
        self.channels_list = self._get_channels_objects(channels_loader_adaptor)
        self.client = client

    async def _get_channels_objects(self, channels_loader: BaseChannelsLoader) -> list:
        channels_list = list()

        for channel_info in channels_loader.get_all():
            if channel_info.private:
                channel = await self.get_private_channel(channel_info)
            else:
                channel = await self.get_public_channel(channel_info)

            if channel:
                channels_list.append(channel)
        logger.info(f"Channels: {len(channels_list)}")

        return channels_list

    async def get_private_channel(self, channel_info):
        channel = None

        channel_invite = await self.client(CheckChatInviteRequest(channel_info.id))
        if channel_invite:
            if isinstance(channel_invite, ChatInvite):
                channel_updates = await self.client(functions.messages.ImportChatInviteRequest(channel_info.id))
                channel = channel_updates.chats[0]
            elif isinstance(channel_invite, ChatInviteAlready):
                channel = channel_invite.chat
            if channel:
                channel = await self._get_chat_obj(channel.id)
        return channel

    async def get_public_channel(self, channel_info):
        channel = await self._get_chat_obj(channel_info.id)
        return channel

    async def start_commenting(self, comments: list):
        for channel in await self.channels_list:
            logger.info(f"Try left comment to channel({channel.id})")
            comment = random.choices(comments)[0]

            messages = await self.get_last_messages(channel=channel, limit=1)
            if not messages:
                logger.warning(f"Empty messages list in channel({channel.id})")
                continue

            discussion_msg = await self.get_random_discussion_message(channel=channel, messages=messages)
            if not discussion_msg:
                logger.error(f"Could not get any discussion message from messages in channel({channel.id})")
                continue

            discussion_channel = await self._get_chat_obj(discussion_msg.chats[0].id)
            commenting_result = await self.commenting_message(channel=discussion_channel, comment=comment,
                                                              message_id=discussion_msg.messages[0].id)
            if not commenting_result:
                logger.warning(
                    f"Could not leave a comment message({discussion_msg.messages[0].id}) in channel({channel.id})")
                continue
            logger.info(f"Successfully added comment to channel({channel.id})!")

    async def get_last_messages(self, channel, limit=10) -> list:
        offset_msg = 0
        all_messages = []
        limit_per_request = self.MESSAGES_LIMIT if limit > self.MESSAGES_LIMIT else limit

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

            if not history.messages:
                break
            messages = history.messages

            for message in messages:
                all_messages.append(message.to_dict())

            offset_msg = messages[len(messages) - 1].id
            total_messages = len(all_messages)

            if limit and total_messages >= limit:
                break
        return all_messages

    async def get_random_discussion_message(self, channel, messages):
        messages = messages.copy()
        random.shuffle(messages)

        for message in messages:
            try:
                discussion_msg = await self.client(
                    functions.messages.GetDiscussionMessageRequest(peer=channel.id,
                                                                   msg_id=message['id']))
                return discussion_msg
            except Exception as e:
                logger.warning(e)
        return

    async def commenting_message(self, channel, comment, message_id):
        try:
            result = None
            if comment.file_path:
                media = None
                file_name = comment.file_path.split("\\")[-1]
                file_extension = comment.file_path.split(".")[-1]

                if comment.file_type == FileTypes.IMAGE:
                    media = types.InputMediaUploadedPhoto(
                                file=await self.client.upload_file(comment.file_path),
                                ttl_seconds=42
                            )
                elif comment.file_type == FileTypes.TEXT_DOCUMENT:
                    media = types.InputMediaUploadedDocument(
                                file=await self.client.upload_file(comment.file_path),
                                ttl_seconds=42,
                                mime_type=f'text/{file_extension}',
                                attributes=[DocumentAttributeFilename(file_name)]
                            )
                elif comment.file_type == FileTypes.APPLICATION_DOCUMENT:
                    media = types.InputMediaUploadedDocument(
                                file=await self.client.upload_file(comment.file_path),
                                ttl_seconds=42,
                                mime_type=f'application/{file_extension}',
                                attributes=[DocumentAttributeFilename(file_name)]
                            )
                elif comment.file_type == FileTypes.VIDEO:
                    media = types.InputMediaUploadedDocument(
                                file=await self.client.upload_file(comment.file_path),
                                ttl_seconds=42,
                                mime_type=f'video/{file_extension}',
                                attributes=[DocumentAttributeFilename(file_name)]
                            )

                if media:
                    result = await self.client(functions.messages.SendMediaRequest(
                        peer=channel,
                        media=media,
                        message=comment.message,
                        reply_to_msg_id=message_id))
            else:
                result = await self.client(functions.messages.SendMessageRequest(peer=channel,
                                                                                 message=comment.message,
                                                                                 reply_to_msg_id=message_id))
            return result
        except Exception as e:
            logger.error(e)
        return

    async def _get_full_chat_obj(self, channel_id):
        try:
            channel_obj = await self.client(functions.channels.GetFullChannelRequest(
                channel=channel_id
            ))
        except Exception as e:
            logger.error(e)
            return

        return channel_obj

    async def _get_chat_obj(self, channel_id):
        try:
            channel_obj = await self.client(functions.channels.GetChannelsRequest(
                id=[channel_id]
            ))
        except Exception as e:
            logger.info(e)
            return None
        return channel_obj.chats[0]
