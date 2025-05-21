import pytest

from currency_exchange.currency_exchange.application.dto import (
	GetExchangeRateDto,
	MakeConvertionDto,
)
from currency_exchange.currency_exchange.application.interactions.exchangeratesinteracions import (
	GetExchangeRateInteraction,
	ConvertCurrencyInteraction,
)
from currency_exchange.currency_exchange.domain.types import CurrencyCode
from currency_exchange.currency_exchange.application.interactions.erfetchstrategies import (
	ExchangeRateFetchStrategy as ERFetchStrat,
)
from currency_exchange.currency_exchange.domain.types import CurrencyAmount
from currency_exchange.currency_exchange.application import errors

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
async def get_exchange_rate_interaction(
	exchange_rates_repo, currencies_repo
) -> GetExchangeRateInteraction:
	return GetExchangeRateInteraction(exchange_rates_repo, currencies_repo)


@pytest.fixture(scope="module")
async def convert_currency_interaction(
	exchange_rates_repo, currencies_repo
) -> ConvertCurrencyInteraction:
	return ConvertCurrencyInteraction(exchange_rates_repo, currencies_repo)


async def test_get_exchange_rate_interaction_by_reversed_rate_successful(
	get_exchange_rate_interaction, exchange_rates_models
):
	res = await get_exchange_rate_interaction(
		GetExchangeRateDto(CurrencyCode("USD"), CurrencyCode("EUR")),
		rate_fetch_strategy=ERFetchStrat.BY_STRAIGHT_RATE,
	)

	assert res.rate.value == pytest.approx(
		exchange_rates_models[("USD", "EUR")].value.value
	)


async def test_get_exchange_rate_interaction_by_common_rate_successful(
	get_exchange_rate_interaction, exchange_rates_models
):
	res = await get_exchange_rate_interaction(
		GetExchangeRateDto(CurrencyCode("EUR"), CurrencyCode("RUB")),
		rate_fetch_strategy=ERFetchStrat.BY_COMMON_CURRENCY,
	)

	assert res.base_currency.code == "EUR"
	assert res.target_currency.code == "RUB"
	assert res.rate.value == pytest.approx(
		exchange_rates_models[("EUR", "USD")].value.value
		/ exchange_rates_models[("RUB", "USD")].value.value
	)


async def test_get_exchange_rate_interaction_rate_with_one_currency_success(
	get_exchange_rate_interaction, exchange_rates_models
):
	res = await get_exchange_rate_interaction(
		GetExchangeRateDto(CurrencyCode("EUR"), CurrencyCode("EUR")),
		rate_fetch_strategy=ERFetchStrat.BY_STRAIGHT_RATE,
	)

	assert res.base_currency.code == "EUR"
	assert res.target_currency.code == "EUR"
	assert res.rate.value == 1


async def test_get_exchange_rate_interaction_error_when_by_straight_rate(
	get_exchange_rate_interaction,
):
	with pytest.raises(errors.ExchangeRateDoesntExistError):
		await get_exchange_rate_interaction(
			GetExchangeRateDto(CurrencyCode("RUB"), CurrencyCode("EUR")),
			rate_fetch_strategy=ERFetchStrat.BY_STRAIGHT_RATE,
		)


async def test_get_exchange_rate_interaction_error_when_by_reversed_rate(
	get_exchange_rate_interaction,
):
	with pytest.raises(errors.ExchangeRateDoesntExistError):
		await get_exchange_rate_interaction(
			GetExchangeRateDto(CurrencyCode("RUB"), CurrencyCode("EUR")),
			rate_fetch_strategy=ERFetchStrat.BY_REVERSED_RATE,
		)


async def test_get_exchange_rate_interaction_error_when_by_common_rate(
	get_exchange_rate_interaction,
):
	with pytest.raises(errors.ExchangeRateDoesntExistError):
		await get_exchange_rate_interaction(
			GetExchangeRateDto(CurrencyCode("KZT"), CurrencyCode("GBP")),
			rate_fetch_strategy=ERFetchStrat.BY_COMMON_CURRENCY,
		)


async def test_convert_currency_interaction_successful_when_cross_rate_is_needed(
	convert_currency_interaction, exchange_rates_models
):
	rate_val = (
		exchange_rates_models["RUB", "USD"].value.value
		/ exchange_rates_models[("EUR", "USD")].value.value
	)
	amount = 10
	res = await convert_currency_interaction(
		MakeConvertionDto(
			CurrencyCode("RUB"), CurrencyCode("EUR"), CurrencyAmount(amount)
		),
		rate_fetch_strategy=ERFetchStrat.BY_COMMON_CURRENCY,
	)
	assert res.base_currency.code == "RUB"
	assert res.target_currency.code == "EUR"
	assert res.exchange_rate.value == pytest.approx(rate_val)
	assert res.target_currency_amount.value == amount * rate_val


async def test_convert_currency_interaction_successful_when_same_base_and_target_currency(
	convert_currency_interaction,
):
	amount = 10
	res = await convert_currency_interaction(
		MakeConvertionDto(
			CurrencyCode("RUB"), CurrencyCode("RUB"), CurrencyAmount(amount)
		),
		rate_fetch_strategy=ERFetchStrat.BY_COMMON_CURRENCY,
	)
	assert res.base_currency.code == "RUB"
	assert res.target_currency.code == "RUB"
	assert res.exchange_rate.value == 1
	assert res.target_currency_amount.value == amount * 1
