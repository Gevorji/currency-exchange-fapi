from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from currency_exchange.currency_exchange.infrastructure.db.dbmodels import (
	CurrencyORMModel,
	CurrenciesExchangeRateORMModel,
)


async def get_currency_from_db(code: str, session: AsyncSession) -> CurrencyORMModel:
	res = await session.scalars(
		select(CurrencyORMModel).where(CurrencyORMModel.code == code)
	)
	return res.one_or_none()


async def get_exchange_rate_from_db(
	basec: str, targetc: str, session: AsyncSession
) -> CurrenciesExchangeRateORMModel:
	base = aliased(CurrencyORMModel)
	target = aliased(CurrencyORMModel)
	res = await session.scalars(
		select(CurrenciesExchangeRateORMModel)
		.join(base, CurrenciesExchangeRateORMModel.base_crncy)
		.where(base.code == basec)
		.join(target, CurrenciesExchangeRateORMModel.target_crncy)
		.where(target.code == targetc)
	)
	return res.one_or_none()
