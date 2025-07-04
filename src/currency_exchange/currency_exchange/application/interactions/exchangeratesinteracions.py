from ..dto import (
	MakeConvertionDto,
	GetExchangeRateDto,
	ExchangeRateDto,
	ConvertedCurrenciesPairDto,
	AlterExchangeRateDto,
	AddExchangeRateDto,
	DeleteExchangeRateDto,
	CurrencyDto,
	GetCurrencyDto,
)

from ...domain.types import CurrencyAmount, ExchangeRateValue
from ..interfaces import ExchangeRatesRepoInterface, CurrencyRepoInterface
from .erfetchstrategies import ExchangeRateFetchStrategy as ERFetchStrat
from .. import errors
from ..extdm import IdentifiedCurrenciesExchangeRate as CurrenciesExchangeRate


class GetAllExchangeRatesInteraction:
	def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
		self._exchange_rates_repo = exchange_rates_repo

	async def __call__(self) -> list[ExchangeRateDto]:
		return [
			ExchangeRateDto.from_dm(er)
			for er in await self._exchange_rates_repo.get_all_rates()
		]


async def _get_exchange_rate(
	rate_data: GetExchangeRateDto,
	exchange_rates_repo: ExchangeRatesRepoInterface,
	currencies_repo: CurrencyRepoInterface,
	*,
	rate_fetch_strategy: ERFetchStrat,
) -> CurrenciesExchangeRate:
	if rate_data.base_currency == rate_data.target_currency:
		currency = await currencies_repo.get_currency(
			GetCurrencyDto(rate_data.base_currency)
		)
		return CurrenciesExchangeRate(currency, currency, ExchangeRateValue(1))
	try:
		return await exchange_rates_repo.get_rate(rate_data)
	except errors.ExchangeRateDoesntExistError:
		if rate_fetch_strategy is ERFetchStrat.BY_STRAIGHT_RATE:
			raise

	if ERFetchStrat.BY_REVERSED_RATE in rate_fetch_strategy:
		try:
			reversed_er = await exchange_rates_repo.get_rate(
				GetExchangeRateDto(rate_data.target_currency, rate_data.base_currency)
			)
			rate = reversed_er.get_reversed()
			rate.id = reversed_er.id
			return rate

		except errors.ExchangeRateDoesntExistError:
			if ERFetchStrat.BY_COMMON_CURRENCY not in rate_fetch_strategy:
				raise

	cross_rates = await exchange_rates_repo.get_cross_rates(rate_data)
	if not cross_rates:
		raise errors.ExchangeRateDoesntExistError(
			f"Couldn't find cross-rates for "
			f"{rate_data.base_currency}-{rate_data.target_currency}"
		)
	cross_rates = cross_rates[0]

	rate = cross_rates[0].get_cross_rate(cross_rates[1])
	if rate.base.code != rate_data.base_currency:
		rate = rate.get_reversed()

	return rate


class GetExchangeRateInteraction:
	def __init__(
		self,
		exchange_rates_repo: ExchangeRatesRepoInterface,
		currencies_repo: CurrencyRepoInterface,
	):
		self._exchange_rates_repo = exchange_rates_repo
		self._currencies_repo = currencies_repo

	async def __call__(
		self, rate_data: GetExchangeRateDto, *, rate_fetch_strategy: ERFetchStrat
	) -> ExchangeRateDto:
		return ExchangeRateDto.from_dm(
			await _get_exchange_rate(
				rate_data,
				self._exchange_rates_repo,
				self._currencies_repo,
				rate_fetch_strategy=rate_fetch_strategy,
			)
		)


class AddExchangeRateInteraction:
	def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
		self._exchange_rates_repo = exchange_rates_repo

	async def __call__(self, exchange_rate: AddExchangeRateDto) -> ExchangeRateDto:
		if exchange_rate.base_currency == exchange_rate.target_currency:
			raise errors.CurrencyToSameCurrencyExchangeRateError(
				"Cant't add exchange rate to same currency"
			)
		return ExchangeRateDto.from_dm(
			await self._exchange_rates_repo.save_rate(exchange_rate)
		)


class UpdateExchangeRateInteraction:
	def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
		self._exchange_rates_repo = exchange_rates_repo

	async def __call__(self, update_data: AlterExchangeRateDto) -> ExchangeRateDto:
		return ExchangeRateDto.from_dm(
			await self._exchange_rates_repo.update_rate(update_data)
		)


class DeleteExchangeRateInteraction:
	def __init__(self, exchange_rates_repo: ExchangeRatesRepoInterface):
		self._exchange_rates_repo = exchange_rates_repo

	async def __call__(self, exchange_rate: DeleteExchangeRateDto) -> ExchangeRateDto:
		return ExchangeRateDto.from_dm(
			await self._exchange_rates_repo.delete_rate(exchange_rate)
		)


class ConvertCurrencyInteraction:
	def __init__(
		self,
		exchange_rates_repo: ExchangeRatesRepoInterface,
		currencies_repo: CurrencyRepoInterface,
	):
		self._exchange_rates_repo = exchange_rates_repo
		self._currencies_repo = currencies_repo

	async def __call__(
		self, convertion_data: MakeConvertionDto, *, rate_fetch_strategy: ERFetchStrat
	) -> ConvertedCurrenciesPairDto:
		try:
			rate = await _get_exchange_rate(
				GetExchangeRateDto(
					convertion_data.from_currency, convertion_data.to_currency
				),
				self._exchange_rates_repo,
				self._currencies_repo,
				rate_fetch_strategy=rate_fetch_strategy,
			)
		except errors.ExchangeRateDoesntExistError as e:
			raise errors.CurrenciesConvertionError(
				"Can't convert currencies as no exchange rate was found"
			) from e

		return ConvertedCurrenciesPairDto(
			CurrencyDto.from_dm(rate.base),
			CurrencyDto.from_dm(rate.target),
			rate.rate,
			convertion_data.amount,
			CurrencyAmount(rate.convert(convertion_data.amount)),
		)
