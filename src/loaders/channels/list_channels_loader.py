from . import BaseChannelsLoader
from models import ChannelLoaderModel


class ListChannelsLoader(BaseChannelsLoader):

    def __init__(self):
        self._channels_ids_list = [ChannelLoaderModel(id="bwt_commentator_test_1", private=False),
                                   ChannelLoaderModel(id="If7N8EnSEWViYzgy", private=True)]

    def get_all(self) -> list:
        return self._channels_ids_list
