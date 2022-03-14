from commentator import Commentator
from loaders.channels import ListChannelsLoader
from loaders.comments import ListCommentsLoader
import logging
from utils import get_configurations
from telethon.sync import TelegramClient


def run_and_return_client(config):
    api_id = int(config['Telegram']['api_id'])
    api_hash = config['Telegram']['api_hash']
    username = config['Telegram']['username']
    is_proxy_enabled = int(config['Proxy']['proxy_enabled'])

    if is_proxy_enabled:
        proxy = {
            'proxy_type': config['Proxy']['proxy_type'],  # (mandatory) protocol to use (see above)
            'addr': config['Proxy']['addr'],  # (mandatory) proxy IP address
            'port': config['Proxy']['port'],  # (mandatory) proxy port number
            'username': config['Proxy']['username'],  # (optional) username if the proxy requires auth
            'password': config['Proxy']['password'],  # (optional) password if the proxy requires auth
            'rdns': True  # (optional) whether to use remote or local resolve, default remote
        }
        client = TelegramClient(username, api_id, api_hash, proxy=proxy)
    else:
        client = TelegramClient(username, api_id, api_hash)
    client.start()
    return client


def main():
    config = get_configurations()

    comments_loader = ListCommentsLoader(config)
    channels_loader = ListChannelsLoader()
    client = run_and_return_client(config)
    commentator = Commentator(client, comments_loader, channels_loader)
    commentator.run_until_complete()


if __name__ == "__main__":
    logging.basicConfig(filename="telegram_commentator.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s [%(levelname)s]: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    main()
