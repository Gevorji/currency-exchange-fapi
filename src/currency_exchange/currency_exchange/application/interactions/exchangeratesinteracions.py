from ..dto import (
    MakeConvertionDto, GetExchangeRateDto, ExchangeRateDto, ConvertedCurrenciesPairDto,
    AlterExchangeRateDto, AddExchangeRateDto, DeleteExchangeRateDto
)
from ..interfaces import ExchangeRatesRepoInterface
from .erfetchstrategies import ExchangeRateFetchStrategy as ERFetchStrat
from .. import errors


class GetAllExchangeRatesInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
        self._exchange_rates_repo = exchange_rates_repo

    async def __call__(self) -> list[ExchangeRateDto]:
        return [ExchangeRateDto.from_dm(er) for er in await self._exchange_rates_repo.get_all_rates()]


class GetExchangeRateInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
        self._exchange_rates_repo = exchange_rates_repo

    async def __call__(
            self, rate_data: GetExchangeRateDto, *, rate_fetch_strategy: ERFetchStrat
    ) -> ExchangeRateDto:
        try:
            return ExchangeRateDto.from_dm(await self._exchange_rates_repo.get_rate(rate_data))
        except errors.ExchangeRateDoesntExistError:
            if rate_fetch_strategy is ERFetchStrat.BY_STRAIGHT_RATE:
                raise

        if ERFetchStrat.BY_REVERSED_RATE in rate_fetch_strategy:
            try:
                return ExchangeRateDto.from_dm(
                    await self._exchange_rates_repo.get_rate(
                        GetExchangeRateDto(rate_data.target_currency, rate_data.base_currency)
                    )
                )
            except errors.ExchangeRateDoesntExistError:
                if ERFetchStrat.BY_COMMON_CURRENCY not in rate_fetch_strategy:
                    raise


        cross_rates = await self._exchange_rates_repo.get_cross_rates(rate_data)
        cross_rates = cross_rates[0]

        rate = cross_rates[0].get_cross_rate(cross_rates[1])
        if rate.base.code != rate_data.base_currency:
            rate = rate.get_reversed()

        return ExchangeRateDto.from_dm(rate)


class AddExchangeRateInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
        self._exchange_rates_repo = exchange_rates_repo

    async def __call__(self, exchange_rate: AddExchangeRateDto) -> ExchangeRateDto:
        return ExchangeRateDto.from_dm(await self._exchange_rates_repo.save_rate(exchange_rate))


class UpdateExchangeRateInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
        self._exchange_rates_repo = exchange_rates_repo

    async def __call__(self, update_data: AlterExchangeRateDto) -> ExchangeRateDto:
        return ExchangeRateDto.from_dm(await self._exchange_rates_repo.update_rate(update_data))


class DeleteExchangeRateInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
        self._exchange_rates_repo = exchange_rates_repo

    async def __call__(self, exchange_rate: DeleteExchangeRateDto) -> ExchangeRateDto:
        return ExchangeRateDto.from_dm(await self._exchange_rates_repo.delete_rate(exchange_rate))


class ConvertCurrencyInteraction:

    def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface, get_exchange_rate: GetExchangeRateInteraction):
        self._exchange_rates_repo = exchange_rates_repo
        self._get_exchange_rate = get_exchange_rate

    async def __call__(
            self, convertion_data: MakeConvertionDto, *, rate_fetch_strategy: ERFetchStrat
    ) -> ConvertedCurrenciesPairDto:
        try:
            rate = await self._get_exchange_rate(
                GetExchangeRateDto(convertion_data.from_currency, convertion_data.to_currency),
                rate_fetch_strategy=rate_fetch_strategy
            )
        except errors.ExchangeRateDoesntExistError as e:
            raise errors.CurrenciesConvertionError(f'Can\'t convert currencies as '
                                                   f'no straight exchange rate was found') from e

        return ConvertedCurrenciesPairDto(
            rate.base_currency, rate.target_currency,
            rate, convertion_data.amount, rate.value * convertion_data.amount
        )
