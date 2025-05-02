from collections import defaultdict
from enum import Enum

from currency_exchange.config import permissions_settings

class UserCategory(Enum):
    API_CLIENT = 'API_CLIENT'
    ANONYMOUS_CLIENT = 'ANONYMOUS_CLIENT'
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'


class OAuthScopeRegistry:
    _scopes: dict[str, str]
    _categories_scopes: dict[UserCategory, list[str]]

    def __init__(self, scopes: dict[str, str]) -> None:
        self._scopes = scopes
        self._categories_scopes = defaultdict(list)

    def get_all_scopes(self) -> list[str]:
        return [k for k in self._scopes.keys()]

    def get_all_scopes_described(self) -> dict[str, str]:
        return self._scopes.copy()

    def add_scope(self, scope: str, description: str = '') -> None:
        self._scopes[scope] = description

    def add_scopes(self, scopes: dict[str, str]) -> None:
        self._scopes.update(scopes)

    def define_standard_scopes_for(self, user_category: UserCategory, scopes: list[str]) -> None:
        self._check_scopes_is_registered(set(scopes))
        self._categories_scopes[user_category] = scopes

    def add_standard_scopes_for(self, user_category: UserCategory, scopes: list[str]):
        self._check_scopes_is_registered(set(scopes))
        self._categories_scopes[user_category].extend(scopes)

    def get_standard_scopes_for(self, user_category: UserCategory) -> list[str]:
        return self._categories_scopes[user_category][:] # copying a list

    def _check_scopes_is_registered(self, scopes: set[str]) -> None:
        diff = scopes.difference(set(self._scopes.keys()))
        if diff:
            raise ValueError(f'No scopes defined inside registry: {diff}')


def get_scopes_registry_from_conf(config):
    registry = OAuthScopeRegistry(config.scopes)

    for user_category, scopes in config.scopes_usr_category_bindings.items():
        registry.define_standard_scopes_for(UserCategory[user_category], scopes)

    return registry


scopes_registry = get_scopes_registry_from_conf(permissions_settings)
