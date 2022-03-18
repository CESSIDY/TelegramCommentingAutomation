from abc import ABC, abstractmethod
from typing import List
from .accounts_model import AccountsLoaderModel


class BaseAccountsLoader(ABC):
    _accounts_list: List[AccountsLoaderModel]

    @abstractmethod
    def get_all(self) -> List[AccountsLoaderModel]:
        pass
