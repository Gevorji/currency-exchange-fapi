from dataclasses import dataclass, field, InitVar
from typing import Optional

from .extdm import (
    IdentifiedCurrency as Currency, IdentifiedCurrenciesExchangeRate as CurrenciesExchangeRate
)
from ..domain.types import ExchangeRateValue, CurrencyCode, CurrencyName, CurrencySign, CurrencyAmount


@dataclass(slots=True)
class CurrencyDto:
    code: CurrencyCode
    name: CurrencyName
    sign: CurrencySign
    id: Optional[int] = None

    @classmethod
    def from_dm(cls, dm: Currency):
        return cls(code=dm.code, name=dm.name, sign=dm.sign, id=dm.id)


@dataclass(slots=True)
class ExchangeRateDto:
    base_currency: CurrencyDto
    target_currency: CurrencyDto
    rate: ExchangeRateValue
    id: Optional[int] = None

    @classmethod
    def from_dm(cls, dm: CurrenciesExchangeRate):
        return cls(
            base_currency=CurrencyDto.from_dm(dm.base),
            target_currency=CurrencyDto.from_dm(dm.target), rate=dm.rate, id=dm.id
        )


@dataclass(slots=True)
class ConvertedCurrenciesPairDto:
    base_currency: CurrencyDto
    target_currency: CurrencyDto
    exchange_rate: ExchangeRateValue
    base_currency_amount: CurrencyAmount
    target_currency_amount: CurrencyAmount


@dataclass(slots=True)
class AddCurrencyDto:
    code: CurrencyCode
    name: CurrencyName
    sign: CurrencySign


@dataclass(slots=True)
class AddExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode
    rate: ExchangeRateValue
    amount: InitVar[CurrencyAmount] = field(default=CurrencyAmount(1))

    def __post_init__(self, amount):
        self.rate = ExchangeRateValue(self.rate.value * amount.value)

@dataclass(slots=True)
class AlterCurrencyDto:
    code: CurrencyCode
    new_name: Optional[CurrencyName] = None
    new_sign: Optional[CurrencySign] = None


@dataclass(slots=True)
class AlterExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode
    new_rate: ExchangeRateValue
    amount: InitVar[CurrencyAmount] = field(default=CurrencyAmount(1))

    def __post_init__(self, amount):
        self.new_rate = ExchangeRateValue(self.new_rate.value * amount.value)


@dataclass(slots=True)
class DeleteCurrencyDto:
    code: CurrencyCode


@dataclass(slots=True)
class DeleteExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode


@dataclass(slots=True)
class GetCurrencyDto:
    code: Optional[CurrencyCode] = None
    name:  Optional[CurrencyName] = None


@dataclass(slots=True)
class GetExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode


@dataclass(slots=True)
class MakeConvertionDto:
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    amount: CurrencyAmount

