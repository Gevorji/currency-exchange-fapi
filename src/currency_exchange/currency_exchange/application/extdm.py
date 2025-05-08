from dataclasses import dataclass

from ..domain.entities import Currency, CurrenciesExchangeRate


@dataclass(frozen=True)
class IdentifiedCurrency(Currency):
    id: int = None


@dataclass
class IdentifiedCurrenciesExchangeRate(CurrenciesExchangeRate):
    base: IdentifiedCurrency | Currency
    target: IdentifiedCurrency | Currency
    id: int = None