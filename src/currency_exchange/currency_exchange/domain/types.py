from collections import UserString
from typing import Any

from . import errors


class CurrencyCode(UserString):

    def __init__(self, code: str, *args: Any, **kwargs: Any) -> None:
        if not code.isalpha() or len(code) != 3:
            raise errors.IncorrectCurrencyCodeError("Currency code must consist of 3 alphabetic characters")
        super().__init__(code.upper(), *args, **kwargs)


class CurrencyName(UserString): ...


class CurrencySign(UserString): ...


class ExchangeRateValue:

    def __init__(self, value: int | float):
        if not value > 0 or value in [float("inf"), float("-inf")]:
            raise errors.IncorrectExchangeRateValue(f'Invalid value for exchange rate {value}')
        self.value = value


class CurrencyAmount:
    def __init__(self, value: int | float):
        if not value > 0 or value in [float("inf"), float("-inf")]:
            raise errors.IncorrectCurrencyAmount(f'Invalid currency amount: {value}')
        self.value = value