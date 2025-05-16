from collections import UserString
from decimal import Decimal
from typing import Any
from string import ascii_letters

from . import errors


class CurrencyCode(UserString):

    def __init__(self, code: str, *args: Any, **kwargs: Any) -> None:
        if not code.isalpha() or len(code) != 3 or not set(code).issubset(ascii_letters):
            raise errors.IncorrectCurrencyCodeError("Currency code must consist of 3 alphabetic characters")
        super().__init__(code.upper(), *args, **kwargs)


class CurrencyName(UserString):
    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        if len(name) == 0:
            raise errors.IncorrectCurrencyName("Currency name cannot be blank")
        super().__init__(name, *args, **kwargs)


class CurrencySign(UserString):
    def __init__(self, sign: str, *args: Any, **kwargs: Any) -> None:
        if len(sign) == 0:
            raise errors.IncorrectCurrencySign("Currency sign cannot be blank")
        super().__init__(sign, *args, **kwargs)


class ExchangeRateValue:

    def __init__(self, value: int | float | Decimal):
        if not value > 0 or value in [float("inf"), float("-inf")]:
            raise errors.IncorrectExchangeRateValue(f'Invalid value for exchange rate {value}')
        self.value = value


class CurrencyAmount:
    def __init__(self, value: int | float):
        if not value > 0 or value in [float("inf"), float("-inf")]:
            raise errors.IncorrectCurrencyAmount(f'Invalid currency amount: {value}')
        self.value = value