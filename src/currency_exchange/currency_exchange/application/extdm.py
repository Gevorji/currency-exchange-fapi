from dataclasses import dataclass
from typing import Optional

from ..domain.entities import Currency, CurrenciesExchangeRate


@dataclass(frozen=True)
class IdentifiedCurrency(Currency):
    id: Optional[int] = None


@dataclass
class IdentifiedCurrenciesExchangeRate(CurrenciesExchangeRate):
    base: IdentifiedCurrency | Currency
    target: IdentifiedCurrency | Currency
    id: Optional[int] = None