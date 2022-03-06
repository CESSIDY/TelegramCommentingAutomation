from commentator import Commentator
from loaders.channels import JsonChannelsLoader
from loaders.comments import JsonCommentsLoader
import logging


def main():
    comments_loader = JsonCommentsLoader()
    channels_loader = JsonChannelsLoader()

    commentator = Commentator(comments_loader, channels_loader)
    commentator.run_until_complete()


if __name__ == "__main__":
    logging.basicConfig(filename="telegram_commentator.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s [%(levelname)s]: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    main()
