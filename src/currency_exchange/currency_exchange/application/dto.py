from dataclasses import dataclass, field
from typing import Optional

from ..domain.entities import CurrencyCode, CurrencyName, CurrencySign
from .extdm import (
    IdentifiedCurrency as Currency, IdentifiedCurrenciesExchangeRate as CurrenciesExchangeRate
)


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
    value: int | float
    id: Optional[int] = None

    @classmethod
    def from_dm(cls, dm: CurrenciesExchangeRate):
        return cls(
            base_currency=CurrencyDto.from_dm(dm.base),
            target_currency=CurrencyDto.from_dm(dm.target), value=dm.value
        )


@dataclass(slots=True)
class ConvertedCurrenciesPairDto:
    base_currency: CurrencyDto
    target_currency: CurrencyDto
    exchange_rate: ExchangeRateDto
    base_currency_amount: int | float
    target_currency_amount: int | float


@dataclass(slots=True)
class AddCurrencyDto:
    code: CurrencyCode
    name: CurrencyName
    sign: CurrencySign


@dataclass(slots=True)
class AddExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode
    value: int | float
    amount: int | float = field(default=1)


@dataclass(slots=True)
class AlterCurrencyDto:
    code: CurrencyCode
    new_name: Optional[CurrencyName] = None
    new_sign: Optional[CurrencySign] = None


@dataclass(slots=True)
class AlterExchangeRateDto:
    base_currency: CurrencyCode
    target_currency: CurrencyCode
    new_value: int | float
    amount: int | float = field(default=1)


@dataclass(slots=True)
class DeleteCurrencyDto:
    code: CurrencyCode


@dataclass(slots=True)
class DeleteExchangeRateDto(DeleteCurrencyDto):
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
    amount: int | float

