from dataclasses import dataclass, field, InitVar
from decimal import Decimal
from email.policy import default
from typing import Optional, Any
from collections import UserString

from . import errors


class CurrencyCode(UserString):

    def __init__(self, code: str, *args: Any, **kwargs: Any) -> None:
        if not code.isalpha() or len(code) != 3:
            raise errors.IncorrectCurrencyCodeError("Currency code must consist of 3 alphabetic characters")
        super().__init__(code.upper(), *args, **kwargs)
        

class CurrencyName(UserString): ...


class CurrencySign(UserString): ...


@dataclass(slots=True, frozen=True)
class Currency:
    code: CurrencyCode
    sign: CurrencySign
    name: CurrencyName

    def __hash__(self):
        return hash(self.code)


@dataclass(slots=True)
class CurrenciesExchangeRate:
    base: Currency
    target: Currency
    value: int | float
    amount: InitVar[int | float] = 1
    decimal_fmt_precision: int = field(kw_only=True, default=2)

    def __post_init__(self, amount):
        self.value = self.value / amount

    def get_reversed(self, *, as_decimal: bool = False, precision: int = None) -> 'CurrenciesExchangeRate':
        reversed_value = 1/self.value
        if as_decimal:
            reversed_value = self._to_decimal_value(reversed_value, precision)
        return self.__class__(
            self.target, self.base, reversed_value,
            decimal_fmt_precision=precision or self.decimal_fmt_precision
        )

    def _to_decimal_value(self, value: int | float, precision: int = None) -> Decimal:
        precision = precision or self.decimal_fmt_precision
        return round(Decimal(str(value)), precision)

    def as_decimal(self, precision: int = None) -> 'CurrenciesExchangeRate':
        return self.__class__(
            self.base, self.target, self._to_decimal_value(self.value, precision),
            decimal_fmt_precision=precision or self.decimal_fmt_precision
        )

    def convert(self, amount: int | float) -> int | float:
        return self.value * amount

    def get_cross_rate(self, exchange_rate: 'CurrenciesExchangeRate', precision: int = None):
        common = {self.base.code, self.target.code}.intersection({exchange_rate.base.code, exchange_rate.target.code})
        if len(common) != 1:
            raise errors.CrossExchangeRateComputationError(f'Cross rate cannot be computed for {self}, {exchange_rate}')
        common = common.pop()

        rate1_normalized = self.get_reversed() if self.base.code == common else self
        rate2_normalized = exchange_rate.get_reversed() if exchange_rate.base.code == common else exchange_rate

        return self.__class__(
            rate1_normalized.base, rate2_normalized.base,
            rate1_normalized.value / rate2_normalized.value,
            decimal_fmt_precision=precision or self.decimal_fmt_precision
        )

    def __str__(self) -> str:
        return f'<Currencies exchange rate: {self.base.code}-{self.target}, value: {self.value}>'