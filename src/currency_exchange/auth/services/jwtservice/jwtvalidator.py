import binascii
from pathlib import Path
from typing import Optional

import joserfc.errors
import pydantic
from joserfc import jwt

from .jwtissuer import LoadKeyMixin, KeyDataType
from .jwtmodel import JWTModel
from . import JWTAlgorithms
from ... import errors


class JWTValidator(LoadKeyMixin):

     def __init__(
             self, key: Optional[KeyDataType] = None, key_path: Optional[str | Path] = None,
             algorithm: JWTAlgorithms = JWTAlgorithms.RS256
     ) -> None:
         self._key = self._load_key(key, key_path)
         self._algorithm = algorithm

     @classmethod
     def from_config(cls, config, **kwargs):
         init_args = {
             'key_path': getattr(config, 'JWT_PUB_KEY_PATH', None),
             'algorithm': getattr(config, 'JWT_SIGN_ALGORITHM', JWTAlgorithms.RS256),
         }
         init_args.update(kwargs)
         return cls(**init_args)

     def token_validate(self, token: str) -> JWTModel:
        token_obj = self._decode_jwt_data(token)
        try:
         return JWTModel.model_validate(
             {
                 'header': token_obj.header,
                 'claims': token_obj.claims,
             }
         )
        except pydantic.ValidationError as e:
         errors.InvalidTokenClaimError(
             '; '.join(f'{err['loc']}: {err['msg']}' for err in e.errors()), token_obj.claims, token_obj.header
         )
        except errors.JWTValidationError as e:
            e.header = token_obj.header
            e.payload = token_obj.claims
            raise e

     def _decode_jwt_data(self, token: str):
         try:
            return jwt.decode(token, self._key, algorithms=[self._algorithm.value])
         except joserfc.errors.BadSignatureError as e:
             raise errors.BadSignatureError('Invalid token with bad signature') from e
         except (binascii.Error, ValueError) as e:
             raise errors.CorruptedTokenDataError('Token data is corrupted') from e
