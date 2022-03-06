from . import BaseChannelsLoader


class JsonChannelsLoader(BaseChannelsLoader):

    def __init__(self):
        self._channels_ids_list = [{"id": "https://t.me/bwt_commentator_test_1", "private": True},
                                   {"id": "r4lRHlcnWAYzNzRi", "private": False}]

    def get_all(self) -> list:
        return self._channels_ids_list
