from abc import ABC, abstractmethod
import re

import bcrypt

from currency_exchange.config import auth_settings
from utils.importobject import import_object

ENCODING = 'utf-8'
PASSWORD_COMPONENTS_EXTRACTION_PATTERN = re.compile('<(.+?)>\\$<(.+?)>')

class HasherInterface(ABC):
    @classmethod
    def get_name(cls) -> str:
        return getattr(cls, 'NAME', cls.__name__)

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def match_hash(self, hash_: str, password: str) -> bool:
        pass


class BCryptHasher(HasherInterface):

    @classmethod
    def hash_password(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(ENCODING), salt).decode(ENCODING)

    @classmethod
    def match_hash(cls, hash_: str, password: str, encoding=ENCODING) -> bool:
        return bcrypt.checkpw(password.encode(encoding), hash_.encode(encoding))


def build_password_string(*password_components) -> str:
    return '$'.join(f'<{component}>' for component in password_components)

def get_password_components(password: str) -> tuple:
    return re.match(PASSWORD_COMPONENTS_EXTRACTION_PATTERN, password).groups()

def get_all_password_hashers():
    return [import_object(obj_str) for obj_str in auth_settings.PASSWORD_HASHERS]

def match_password(password: str, hashed_password: str) -> bool:
    hasher_name, pswd_hash = get_password_components(hashed_password)
    for hasher in get_all_password_hashers():
        if hasher.get_name() == hasher_name:
            return hasher.match_hash(pswd_hash, password)

def get_password_hash_str(password: str):
    hasher = get_all_password_hashers()[0]
    return build_password_string(hasher.get_name(), hasher.hash_password(password))

