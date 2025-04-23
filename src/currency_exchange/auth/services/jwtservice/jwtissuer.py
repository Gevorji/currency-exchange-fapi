import datetime
import json
from math import ceil
from pathlib import Path
from typing import Optional, Tuple, Any
from uuid import uuid4

from joserfc import jwt, jwk

from . import JWTAlgorithms

KeyDataType = str | bytes | dict[str, str | list[str]]
KeyType = jwk.RSAKey | jwk.OctKey | jwk.ECKey


class LoadKeyMixin:
    _ALGORITHM_KEY_TYPE = {
        JWTAlgorithms.HS256: 'oct',
        JWTAlgorithms.RS256: 'RSA',
        JWTAlgorithms.ES256: 'ES',
    }

    _algorithm: JWTAlgorithms = JWTAlgorithms.RS256

    def _load_key(self, key: KeyDataType | None, key_path: str | Path | None):
        if not (key_path or key):
            raise ValueError('Either key or key path must be provided')
        if key:
            return self._load_key_from_data(key)
        else:
            return self._load_key_from_file(key_path)

    def _load_key_from_data(self, key_data: KeyDataType) -> KeyType:
        return jwk.JWKRegistry.import_key(key_data, key_type=self._ALGORITHM_KEY_TYPE[self._algorithm])

    def _load_key_from_file(self, key_path: str | Path) -> KeyType:
        if isinstance(key_path, str):
            key_path = Path(key_path)
        with open(key_path) as f:
            if key_path.suffix == '.json':
                key_data = json.load(f)
            else:
                key_data = f.read()

        return self._load_key_from_data(key_data)


class JWTIssuer(LoadKeyMixin):
    """
    Issues jwts based on given config.

    key is a string, bytes or dict representing the JWT key.
    key_path is a string either a Path object representing the path to the key file. File may store the key in
    a json, pem, der formats.

    If key and key_path both present, key_path will not be taken into account.

    The behaviour for scope and audience params is that if the param were passed during the instantiation
    of JWTIssuer, its value will be inserted into jwt when no custom audience value were passed to the
    get_access_token(), otherwise the custom value will take precedence.

    Subject param should be passed to get_access_token() and get_refresh_token() on each call.

    JWTIssuer.from_config() method creates an instance from given config data class. You may pass some kwargs to it with
    keys corresponding to init args. If any kwargs is present, they will overlap the config variables.

    Private claims may be given on initialization as a key argument whose value is dict of claims and their
    default values. Further, this private claims will be added to every produced token, as well as own private keys dict
    may be passed to each get_access_token() and get_refresh_token() call so that instance level values will
    be overridden. To skip an addition of instance level private claims, dismiss_preset_private_claims flag can be
    passed on method call.
    """

    def __init__(
            self, key: Optional[KeyDataType] = None, key_path: Optional[str | Path] = None, issuer: Optional[str] = None,
            audience: Optional[str | list[str]] = None,
            scope: Optional[str | list[str]] = None,
            access_tkn_duration: Optional[datetime.timedelta] = None,
            refresh_tkn_duration: Optional[datetime.timedelta] = None,
            not_before: Optional[datetime.timedelta] = None, assign_jtis: bool = False,
            algorithm: JWTAlgorithms = JWTAlgorithms.RS256,
            *, private_claims: Optional[dict[str, Any]] = None,
    ) -> None:
        self._algorithm = algorithm
        self._key = self._load_key(key, key_path)
        self._issuer = issuer
        self._audience = audience
        self._scope = scope
        self._refresh_tkn_duration = refresh_tkn_duration
        self._access_tkn_duration = access_tkn_duration
        self._not_before = not_before
        self._assign_jtis = assign_jtis
        self._private_claims = private_claims or {}

    @classmethod
    def from_config(cls, config, *, private_claims: Optional[dict[str, Any]] = None, **kwargs):
        init_args = {
            'key_path': getattr(config, 'JWT_PRIV_KEY_PATH', None),
            'issuer': getattr(config, 'JWT_ISSUER', None),
            'access_tkn_duration': getattr(config, 'JWT_ACCESS_DURATION', None),
            'refresh_tkn_duration': getattr(config, 'JWT_REFRESH_DURATION', None),
            'not_before': getattr(config, 'JWT_NBF_DURATION', None),
            'assign_jtis': getattr(config, 'JWT_JTIS', None),
            'algorithm': getattr(config, 'JWT_SIGN_ALGORITHM', JWTAlgorithms.RS256)
        }
        private_claims = private_claims or {}
        init_args.update(kwargs)
        return cls(**init_args, private_claims=private_claims)

    def config_private_claims(self, **claims):
        self._private_claims.update(claims)

    def _get_token_base(
            self, subject: Optional[str] = None, audience: Optional[str | list[str]] = None,
            duration: Optional[datetime.timedelta] = None, *, private_claims: Optional[dict[str, Any]] = None,
            dismiss_preset_private_claims: bool = False
    ) -> Tuple[dict, dict]:
        private_claims = private_claims or {}
        header = {
            'typ': 'JWT',
            'alg': self._algorithm.value
        }
        issue_time = datetime.datetime.now(tz=datetime.timezone.utc)
        expiry_time = issue_time + duration
        nbf = None
        if self._not_before:
            nbf = issue_time + self._not_before
        payload = {
            'iss': self._issuer,
            'sub': subject,
            'exp': ceil(expiry_time.timestamp()),
            'iat': ceil(issue_time.timestamp()),
        }

        if self._audience or audience:
            payload['aud'] = audience or self._audience
        if nbf:
            payload['nbf'] = ceil(nbf.timestamp())

        if not dismiss_preset_private_claims:
            payload.update(self._private_claims)
        payload.update(private_claims)

        return header, payload

    def _encode_jwt_data(self, tkn_header: dict, tkn_payload: dict) -> str:
        return jwt.encode(tkn_header, tkn_payload, self._key)

    def _assign_jti(self, tkn_payload: dict) -> dict:
        if self._assign_jtis:
            tkn_payload['jti'] = uuid4().hex
        return tkn_payload

    def get_access_token(
            self, subject: Optional[str] = None, audience: Optional[str | list[str]] = None,
            scope: Optional[str | list[str]] = None, *, private_claims: Optional[dict[str, Any]] = None,
            dismiss_preset_private_claims: bool = False
    ) -> tuple[str, dict, dict]:
        header, payload = self._get_token_base(
            subject, audience, self._access_tkn_duration, private_claims=private_claims,
            dismiss_preset_private_claims=dismiss_preset_private_claims
        )
        if self._scope or scope:
            payload['scope'] = list(scope or self._scope)

        self._assign_jti(payload)

        return self._encode_jwt_data(header, payload), header, payload

    def get_refresh_token(
            self, subject: Optional[str] = None,
            audience: Optional[str | list[str]] = None, scope: Optional[str | list[str]] = None,
            *, private_claims: Optional[dict[str, Any]] = None,
            dismiss_preset_private_claims: bool = False
    ) -> tuple[str, dict, dict]:
        header, payload = self._get_token_base(
            subject, audience, self._refresh_tkn_duration, private_claims=private_claims,
            dismiss_preset_private_claims = dismiss_preset_private_claims
        )
        if self._scope or scope:
            payload['scope'] = ['refresh'] + list(scope or self._scope)

        self._assign_jti(payload)

        return self._encode_jwt_data(header, payload), header, payload

    


