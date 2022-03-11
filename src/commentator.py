from loaders.channels import BaseChannelsLoader
from loaders.comments import BaseCommentsLoader
from telethon.sync import TelegramClient
from utils import get_configurations
from managers import ChannelsManager


class Commentator:
    def __init__(self, comments_loader_adaptor: BaseCommentsLoader, channels_loader_adaptor: BaseChannelsLoader):
        self.comments_loader = comments_loader_adaptor
        self.channels_loader = channels_loader_adaptor
        self.config = get_configurations()
        self.client = self.run_and_return_client(self.config)
        self.channels_manager = ChannelsManager(client=self.client, channels_loader_adaptor=self.channels_loader)

    def run_and_return_client(self, config):
        api_id = int(self.config['Telegram']['api_id'])
        api_hash = self.config['Telegram']['api_hash']
        username = self.config['Telegram']['username']
        is_proxy_enabled = int(self.config['Proxy']['proxy_enabled'])

        if is_proxy_enabled:
            proxy = {
                'proxy_type': self.config['Proxy']['proxy_type'],  # (mandatory) protocol to use (see above)
                'addr': self.config['Proxy']['addr'],  # (mandatory) proxy IP address
                'port': self.config['Proxy']['port'],  # (mandatory) proxy port number
                'username': self.config['Proxy']['username'],  # (optional) username if the proxy requires auth
                'password': self.config['Proxy']['password'],  # (optional) password if the proxy requires auth
                'rdns': True  # (optional) whether to use remote or local resolve, default remote
            }
            client = TelegramClient(username, api_id, api_hash, proxy=proxy)
        else:
            client = TelegramClient(username, api_id, api_hash)
        client.start()
        return client

    def run_until_complete(self):
        with self.client:
            self.client.loop.run_until_complete(self.run())

    async def run(self):
        await self.channels_manager.start_commenting(self.comments_loader.get_all())
