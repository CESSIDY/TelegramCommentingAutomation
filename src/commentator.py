from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader
from managers import ChannelsManager


class Commentator:
    def __init__(self, client, comments_loader_adaptor: BaseCommentsLoader, channels_loader_adaptor: BaseChannelsLoader):
        self.comments_loader = comments_loader_adaptor
        self.channels_loader = channels_loader_adaptor
        self.client = client
        self.channels_manager = ChannelsManager(client=self.client, channels_loader_adaptor=self.channels_loader)

    def run_until_complete(self):
        with self.client:
            self.client.loop.run_until_complete(self.run())

    async def run(self):
        await self.channels_manager.start_commenting(self.comments_loader.get_all())
