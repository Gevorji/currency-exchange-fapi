from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from currency_exchange.db.session import async_session_factory
from ..application.dto import (GetCurrencyDto, CurrencyDto, AddCurrencyDto, AlterCurrencyDto, DeleteCurrencyDto,
                               ExchangeRateDto, GetExchangeRateDto, AlterExchangeRateDto, AddExchangeRateDto,
                               DeleteExchangeRateDto, ConvertedCurrenciesPairDto, MakeConvertionDto)
from ..application.interactions.currenciesinteractions import (GetAllCurrenciesInteraction, GetCurrencyInteraction,
                                                               AddCurrencyInteraction, UpdateCurrencyInteraction,
                                                               DeleteCurrencyInteraction)
from ..application.interactions.exchangeratesinteracions import (GetAllExchangeRatesInteraction,
                                                                 GetExchangeRateInteraction, AddExchangeRateInteraction,
                                                                 UpdateExchangeRateInteraction,
                                                                 DeleteExchangeRateInteraction,
                                                                 ConvertCurrencyInteraction)
from ..application.interactions.erfetchstrategies import ExchangeRateFetchStrategy as ERFetchStrat
from ..domain.types import CurrencyCode, CurrencyName, CurrencySign, ExchangeRateValue, CurrencyAmount
from ..infrastructure.db.repos import CurrencyPostgresRepo, ExchangeRatesPostgresRepo
from .schemas import AddCurrencySchema, UpdateCurrencySchema, AddExchangeRateSchema


class CurrencyExchangeFastAPIAdapter:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._currencies_repo = CurrencyPostgresRepo(session_factory)
        self._exchange_rates_repo = ExchangeRatesPostgresRepo(session_factory)
        self._app_layer_interactions = {
            GetAllCurrenciesInteraction: GetAllCurrenciesInteraction(self._currencies_repo),
            GetCurrencyInteraction: GetCurrencyInteraction(self._currencies_repo),
            AddCurrencyInteraction: AddCurrencyInteraction(self._currencies_repo),
            UpdateCurrencyInteraction: UpdateCurrencyInteraction(self._currencies_repo),
            DeleteCurrencyInteraction: DeleteCurrencyInteraction(self._currencies_repo),
            GetAllExchangeRatesInteraction: GetAllExchangeRatesInteraction(self._exchange_rates_repo),
            GetExchangeRateInteraction: GetExchangeRateInteraction(self._exchange_rates_repo, self._currencies_repo),
            AddExchangeRateInteraction: AddExchangeRateInteraction(self._exchange_rates_repo),
            UpdateExchangeRateInteraction: UpdateExchangeRateInteraction(self._exchange_rates_repo),
            DeleteExchangeRateInteraction: DeleteExchangeRateInteraction(self._exchange_rates_repo),
            ConvertCurrencyInteraction: ConvertCurrencyInteraction(self._exchange_rates_repo, self._currencies_repo)
        }

    def get_interaction(self, interaction):
        return self._app_layer_interactions[interaction]

    async def get_all_currencies(self) -> list[CurrencyDto]:
        return await self.get_interaction(GetAllCurrenciesInteraction)()

    async def get_currency(self, code: str) -> CurrencyDto:
        return await self.get_interaction(GetCurrencyInteraction)(GetCurrencyDto(code=CurrencyCode(code)))

    async def add_currency(self, currency_data: AddCurrencySchema) -> CurrencyDto:
        add_dto=AddCurrencyDto(code=CurrencyCode(currency_data.code),
                       name=CurrencyName(currency_data.name), sign=CurrencySign(currency_data.sign))
        return await self.get_interaction(AddCurrencyInteraction)(add_dto)

    async def update_currency(self, code: str, currency_data: UpdateCurrencySchema) -> CurrencyDto:
        upd_dto = AlterCurrencyDto(CurrencyCode(code), CurrencyName(currency_data.new_name),
                                   CurrencySign(currency_data.new_sign))

        return await self.get_interaction(UpdateCurrencyInteraction)(upd_dto)

    async def delete_currency(self, code: str) -> CurrencyDto:
        return await self.get_interaction(DeleteCurrencyInteraction)(DeleteCurrencyDto(code=CurrencyCode(code)))

    async def get_all_exchange_rates(self) -> list[ExchangeRateDto]:
        return await self.get_interaction(GetAllExchangeRatesInteraction)()

    async def get_exchange_rate(self, base_currency_code: str, target_currency_code: str) -> ExchangeRateDto:
        return await self.get_interaction(GetExchangeRateInteraction)(
            GetExchangeRateDto(CurrencyCode(base_currency_code), CurrencyCode(target_currency_code)),
            rate_fetch_strategy=ERFetchStrat.BY_REVERSED_RATE
        )

    async def add_exchange_rate(self, er_data: AddExchangeRateSchema):
        return await self.get_interaction(AddExchangeRateInteraction)(
            AddExchangeRateDto(CurrencyCode(er_data.baseCurrencyCode), CurrencyCode(er_data.targetCurrencyCode),
                               ExchangeRateValue(er_data.rate))
        )

    async def update_exchange_rate(self, base_currency_code: str,
                                   target_currency_code: str, rate: float) -> ExchangeRateDto:
        return await self.get_interaction(UpdateExchangeRateInteraction)(
            AlterExchangeRateDto(CurrencyCode(base_currency_code), CurrencyCode(target_currency_code),
                                 ExchangeRateValue(rate))
        )

    async def delete_exchange_rate(self, base_currency_code: str, target_currency_code: str) -> ExchangeRateDto:
        return await self.get_interaction(DeleteExchangeRateInteraction)(
            DeleteExchangeRateDto(CurrencyCode(base_currency_code), CurrencyCode(target_currency_code))
        )

    async def convert_currency(self, base_currency_code: str, target_currency_code: str,
                               amount: float) -> ConvertedCurrenciesPairDto:
        strat = ERFetchStrat.BY_STRAIGHT_RATE | ERFetchStrat.BY_REVERSED_RATE | ERFetchStrat.BY_COMMON_CURRENCY
        return await self.get_interaction(ConvertCurrencyInteraction)(
            MakeConvertionDto(CurrencyCode(base_currency_code), CurrencyCode(target_currency_code),
                              CurrencyAmount(amount)),
            rate_fetch_strategy=strat
        )


currency_exchange_app = CurrencyExchangeFastAPIAdapter(async_session_factory)