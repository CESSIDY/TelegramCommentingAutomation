from models import MediaModel, FileTypes
from telethon.tl import types
from telethon.tl.types import DocumentAttributeFilename


class MediaManager:
    TTL_SECONDS = 42

    def __init__(self, client):
        self.client = client

    async def get_media_object(self, media_model: MediaModel):
        media = None
        file_name = media_model.get_file_name()
        file_extension = media_model.get_file_extension()

        if media_model.file_type == FileTypes.IMAGE:
            media = types.InputMediaUploadedPhoto(
                file=await self.client.upload_file(media_model.file_path),
                ttl_seconds=self.TTL_SECONDS
            )
        elif media_model.file_type == FileTypes.TEXT_DOCUMENT:
            media = types.InputMediaUploadedDocument(
                file=await self.client.upload_file(media_model.file_path),
                ttl_seconds=self.TTL_SECONDS,
                mime_type=f'text/{file_extension}',
                attributes=[DocumentAttributeFilename(file_name)]
            )
        elif media_model.file_type == FileTypes.APPLICATION_DOCUMENT:
            media = types.InputMediaUploadedDocument(
                file=await self.client.upload_file(media_model.file_path),
                ttl_seconds=self.TTL_SECONDS,
                mime_type=f'application/{file_extension}',
                attributes=[DocumentAttributeFilename(file_name)]
            )
        elif media_model.file_type == FileTypes.VIDEO:
            media = types.InputMediaUploadedDocument(
                file=await self.client.upload_file(media_model.file_path),
                ttl_seconds=self.TTL_SECONDS,
                mime_type=f'video/{file_extension}',
                attributes=[DocumentAttributeFilename(file_name)]
            )
        return media
