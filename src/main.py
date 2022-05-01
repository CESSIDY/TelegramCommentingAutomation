import logging
import os
from telethon.sync import TelegramClient
from loaders.accounts import JsonAccountsLoader
from loaders.channels import JsonChannelsLoader
from loaders.comments import JsonCommentsLoader
from models import AccountsLoaderModel
from utils import get_configurations
from workers.commentator import Commentator

logging.basicConfig(filename="telegram_commentator.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    config = get_configurations()

    comments_loader = JsonCommentsLoader()
    channels_loader = JsonChannelsLoader()
    accounts_loader = JsonAccountsLoader()
    account_models = accounts_loader.get_all()

    account_models = check_and_init_sessions(account_models, config)
    run_commentator_for_all_accounts(account_models, config, comments_loader, channels_loader)


def check_and_init_sessions(account_models, config) -> [AccountsLoaderModel]:
    temp_account_models = list()

    for account in account_models:
        print(f"Login for: {account.username}")
        try:
            client = run_and_return_client(config, account)
            client.disconnect()
            temp_account_models.append(account)
        except Exception as e:
            print(f"Authorization error for {account.username}")
            logger.error(e)

    return temp_account_models


def run_commentator_for_all_accounts(account_models, config, comments_loader, channels_loader):
    for account in account_models:
        print(f"Start processing for {account.username}")
        client = run_and_return_client(config, account)
        commentator = Commentator(client, comments_loader, channels_loader)
        commentator.run_until_complete()
        client.disconnect()
        print(f"Finish processing for {account.username}")


def run_and_return_client(config, account_model: AccountsLoaderModel):
    config_file_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', "sessions"))

    api_id = account_model.api_id
    api_hash = account_model.api_hash
    username = account_model.username

    session_path = os.path.join(config_file_path, username)

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
        client = TelegramClient(session_path, api_id, api_hash, proxy=proxy)
    else:
        client = TelegramClient(session_path, api_id, api_hash)
    client.start()
    return client


if __name__ == "__main__":
    main()
