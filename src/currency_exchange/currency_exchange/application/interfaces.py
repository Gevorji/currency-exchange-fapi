from typing import Protocol

from .extdm import (
    IdentifiedCurrenciesExchangeRate as CurrenciesExchangeRate, IdentifiedCurrency as Currency
)
from .dto import AddCurrencyDto, AlterCurrencyDto, DeleteCurrencyDto, AddExchangeRateDto, AlterExchangeRateDto, \
    DeleteExchangeRateDto, GetCurrencyDto, GetExchangeRateDto


class CurrencyRepoInterface(Protocol):

    async def get_all_currencies(self) -> list[Currency]: ...

    async def get_currency(self, currency_data: GetCurrencyDto) -> Currency: ...

    async def save_currency(self, currency: AddCurrencyDto) -> Currency: ...

    async def update_currency(self, currency: AlterCurrencyDto) -> Currency: ...

    async def delete_currency(self, currency: DeleteCurrencyDto) -> Currency: ...


class ExchangeRatesRepoInterface(Protocol):

    async def get_all_rates(self) -> list[CurrenciesExchangeRate]: ...

    async def get_rate(self, rate: GetExchangeRateDto) -> CurrenciesExchangeRate: ...

    async def save_rate(self, rate: AddExchangeRateDto) -> CurrenciesExchangeRate: ...

    async def update_rate(self, rate: AlterExchangeRateDto) -> CurrenciesExchangeRate: ...

    async def delete_rate(self, rate: DeleteExchangeRateDto) -> CurrenciesExchangeRate: ...

    async def get_cross_rates(
            self, rate: GetExchangeRateDto
    ) -> list[tuple[CurrenciesExchangeRate, CurrenciesExchangeRate]]: ...
