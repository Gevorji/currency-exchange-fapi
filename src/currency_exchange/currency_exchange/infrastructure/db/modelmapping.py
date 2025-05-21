from ...application.extdm import (
	IdentifiedCurrency as Currency,
	IdentifiedCurrenciesExchangeRate as ExchangeRate,
)
from .dbmodels import CurrencyORMModel, CurrenciesExchangeRateORMModel
from ...domain.types import CurrencyCode, CurrencyName, CurrencySign


def orm_currency_to_dm_currency(currency: CurrencyORMModel) -> Currency:
	code = (
		CurrencyCode(currency.code) if isinstance(currency.code, str) else currency.code
	)
	name = (
		CurrencyName(currency.name) if isinstance(currency.name, str) else currency.name
	)
	sign = (
		CurrencySign(currency.sign) if isinstance(currency.sign, str) else currency.sign
	)
	return Currency(code, sign, name, currency.id)


def orm_ex_rate_to_dm_ex_rate(ex_rate: CurrenciesExchangeRateORMModel) -> ExchangeRate:
	return ExchangeRate(
		base=orm_currency_to_dm_currency(ex_rate.base_crncy),
		target=orm_currency_to_dm_currency(ex_rate.target_crncy),
		id=ex_rate.id,
		rate=ex_rate.value,
	)
