import logging
import os
from telethon.sync import TelegramClient
from loaders.accounts import JsonAccountsLoader
from loaders.channels import JsonChannelsLoader
from loaders.comments import JsonCommentsLoader
from models import AccountsLoaderModel
from utils import session_files_path, get_proxy_configurations, configure_logging
from workers import Commentator
from workers.commentators import CommentingLastUncommentingPostAdaptor

configure_logging()
logger = logging.getLogger(__name__)


def main():
    accounts_loader = JsonAccountsLoader()
    account_models = accounts_loader.get_all()

    account_models = check_and_init_sessions(account_models)
    run_commentator_for_all_accounts(account_models)


def check_and_init_sessions(account_models) -> [AccountsLoaderModel]:
    temp_account_models = list()

    for account in account_models:
        print(f"Login for: {account.username}")
        try:
            client = run_and_return_client(account)
            client.disconnect()
            temp_account_models.append(account)
        except Exception as e:
            print(f"Authorization error for {account.username}")
            logger.error(e)

    return temp_account_models


def run_commentator_for_all_accounts(account_models):
    comments_loader = JsonCommentsLoader()
    channels_loader = JsonChannelsLoader()

    for account in account_models:
        print(f"Start processing for {account.username}")
        client = run_and_return_client(account)

        commenting_adapter = CommentingLastUncommentingPostAdaptor(client, comments_loader)
        commentator = Commentator(client, comments_loader, channels_loader, commenting_adapter)
        commentator.run_until_complete()

        client.disconnect()
        print(f"Finish processing for {account.username}")


def run_and_return_client(account_model: AccountsLoaderModel):
    session_path = os.path.join(session_files_path, account_model.username)

    proxy = get_proxy_configurations()
    if proxy:
        client = TelegramClient(session_path, account_model.api_id, account_model.api_hash, proxy=proxy)
    else:
        client = TelegramClient(session_path, account_model.api_id, account_model.api_hash)

    client.start()
    return client


if __name__ == "__main__":
    main()
