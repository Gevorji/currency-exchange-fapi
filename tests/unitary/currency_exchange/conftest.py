import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from currency_exchange.currency_exchange.domain.types import ExchangeRateValue
from currency_exchange.currency_exchange.infrastructure.db.repos import (
	CurrencyPostgresRepo,
	ExchangeRatesPostgresRepo,
)
from currency_exchange.currency_exchange.infrastructure.db.dbmodels import (
	CurrenciesExchangeRateORMModel,
	CurrencyORMModel,
)


@pytest.fixture(scope="package", autouse=True)
async def currencies_models(db_connection) -> dict[str, CurrencyORMModel]:
	models = [
		CurrencyORMModel(code="EUR", name="Euro", sign="E"),
		CurrencyORMModel(code="USD", name="US Dollar", sign="$"),
		CurrencyORMModel(code="RUB", name="Russian ruble", sign="Р"),
		CurrencyORMModel(code="DKK", name="Danish Krone", sign="D"),
		CurrencyORMModel(code="JPY", name="Yen", sign="Y"),
		CurrencyORMModel(code="KZT", name="Tenge", sign="T"),
		CurrencyORMModel(code="GBP", name="Pound Sterling", sign="£"),
	]

	async with AsyncSession(db_connection, expire_on_commit=False) as session:
		async with session.begin():
			for model in models:
				session.add(model)
	return {currency.code: currency for currency in models}


@pytest.fixture(scope="package", autouse=True)
async def exchange_rates_models(
	db_connection, currencies_models
) -> dict[tuple[str, str], CurrenciesExchangeRateORMModel]:
	models = [
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["EUR"].id,
			target_crncy_id=currencies_models["USD"].id,
			value=ExchangeRateValue(1.13),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["RUB"].id,
			target_crncy_id=currencies_models["USD"].id,
			value=ExchangeRateValue(1 / 100),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["USD"].id,
			target_crncy_id=currencies_models["EUR"].id,
			value=ExchangeRateValue(1 / 1.13),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["EUR"].id,
			target_crncy_id=currencies_models["JPY"].id,
			value=ExchangeRateValue(163),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["RUB"].id,
			target_crncy_id=currencies_models["JPY"].id,
			value=ExchangeRateValue(2),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["DKK"].id,
			target_crncy_id=currencies_models["EUR"].id,
			value=ExchangeRateValue(0.13),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["RUB"].id,
			target_crncy_id=currencies_models["DKK"].id,
			value=ExchangeRateValue(0.081),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["USD"].id,
			target_crncy_id=currencies_models["GBP"].id,
			value=ExchangeRateValue(0.75),
		),
		CurrenciesExchangeRateORMModel(
			base_crncy_id=currencies_models["KZT"].id,
			target_crncy_id=currencies_models["RUB"].id,
			value=ExchangeRateValue(0.16),
		),
	]

	async with AsyncSession(db_connection) as session:
		async with session.begin():
			for model in models:
				session.add(model)
		await session.execute(
			select(CurrenciesExchangeRateORMModel).execution_options(
				populate_existing=True
			)
		)

	return {(er.base_crncy.code, er.target_crncy.code): er for er in models}


@pytest.fixture(scope="module")
async def currencies_repo(local_sessionmaker) -> CurrencyPostgresRepo:
	return CurrencyPostgresRepo(local_sessionmaker)


@pytest.fixture(scope="module")
async def exchange_rates_repo(local_sessionmaker) -> ExchangeRatesPostgresRepo:
	return ExchangeRatesPostgresRepo(local_sessionmaker)
