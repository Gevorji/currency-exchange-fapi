from typing import Sequence
from dataclasses import asdict as dataclass_asdict

from sqlalchemy import select, insert, update, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import sqlalchemy.exc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased

from .modelmapping import orm_currency_to_dm_currency, orm_ex_rate_to_dm_ex_rate
from ...application.errors import ExchangeRateAlreadyExistsError
from ...application.extdm import (
	IdentifiedCurrency as Currency,
	IdentifiedCurrenciesExchangeRate as CurrenciesExchangeRate,
)
from .dbmodels import (
	CurrencyORMModel as CurrencyORM,
	CurrenciesExchangeRateORMModel as ExRateORM,
	CurrenciesExchangeRateORMModel,
)
from ...application.interfaces import CurrencyRepoInterface, ExchangeRatesRepoInterface
from ...application.dto import (
	GetCurrencyDto,
	GetExchangeRateDto,
	AddCurrencyDto,
	AddExchangeRateDto,
	AlterCurrencyDto,
	AlterExchangeRateDto,
	DeleteCurrencyDto,
	DeleteExchangeRateDto,
)
from ...application import errors
from ...domain.entities import CurrencyCode


class CurrencyPostgresRepo(CurrencyRepoInterface):
	def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
		self._session_factory = session_factory

	async def get_all_currencies(self) -> list[Currency]:
		async with self._session_factory() as session:
			res = await session.scalars(select(CurrencyORM))
		return [orm_currency_to_dm_currency(c) for c in res.all()]

	async def get_currency(self, currency_data: GetCurrencyDto) -> Currency:
		if currency_data.code:
			criteria = CurrencyORM.code == currency_data.code.data
			on_exc = f"code {currency_data.code}"
		else:
			criteria = CurrencyORM.name == currency_data.name.data
			on_exc = f"name {currency_data.name}"
		async with self._session_factory() as session:
			res = await session.scalars(select(CurrencyORM).where(criteria))
		try:
			return orm_currency_to_dm_currency(res.one())
		except NoResultFound:
			raise errors.CurrencyDoesNotExistError(f"No currency with {on_exc}")

	async def save_currency(self, currency: AddCurrencyDto) -> Currency:
		async with self._session_factory() as session:
			async with session.begin():
				try:
					res = await session.scalars(
						insert(CurrencyORM).returning(CurrencyORM),
						[
							{
								"code": currency.code.data,
								"name": currency.name.data,
								"sign": currency.sign.data,
							}
						],
					)
				except sqlalchemy.exc.IntegrityError as e:
					raise errors.CurrencyAlreadyExistsError(
						f"Currency with code {currency.code} already exists"
					) from e

		return orm_currency_to_dm_currency(res.one())

	async def update_currency(self, currency: AlterCurrencyDto) -> Currency:
		update_values = {
			k.removeprefix("new_"): v.data
			for k, v in dataclass_asdict(currency).items()
			if v is not None and k != "code"
		}
		async with self._session_factory() as session:
			async with session.begin():
				res = await session.scalars(
					update(CurrencyORM)
					.where(CurrencyORM.code == currency.code.data)
					.values(**update_values)
					.returning(CurrencyORM),
				)
		try:
			return orm_currency_to_dm_currency(res.one())
		except NoResultFound:
			raise errors.CurrencyDoesNotExistError(
				f"No currency with code {currency.code} to alter"
			)

	async def delete_currency(self, currency: DeleteCurrencyDto) -> Currency:
		async with self._session_factory() as session:
			async with session.begin():
				res = await session.scalars(
					delete(CurrencyORM)
					.where(CurrencyORM.code == currency.code.data)
					.returning(CurrencyORM)
				)
		try:
			return orm_currency_to_dm_currency(res.one())
		except NoResultFound:
			raise errors.CurrencyDoesNotExistError(
				f"No currency with code {currency.code} to delete"
			)


class ExchangeRatesPostgresRepo(ExchangeRatesRepoInterface):
	def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
		self._session_factory = session_factory

	async def get_all_rates(self) -> list[CurrenciesExchangeRate]:
		async with self._session_factory() as session:
			res = await session.scalars(select(CurrenciesExchangeRateORMModel))
		return [orm_ex_rate_to_dm_ex_rate(er) for er in res.all()]

	async def get_rate(self, rate: GetExchangeRateDto) -> CurrenciesExchangeRate:
		async with self._session_factory() as session:
			base = aliased(CurrencyORM)
			target = aliased(CurrencyORM)
			res = await session.scalars(
				select(ExRateORM)
				.join(base, ExRateORM.base_crncy)
				.where(base.code == rate.base_currency.data)
				.join(target, ExRateORM.target_crncy)
				.where(target.code == rate.target_currency.data)
			)
		try:
			return orm_ex_rate_to_dm_ex_rate(res.one())
		except NoResultFound:
			raise errors.ExchangeRateDoesntExistError(
				f"No exchange rate for {rate.base_currency}->{rate.target_currency}"
			)

	async def save_rate(self, rate: AddExchangeRateDto) -> CurrenciesExchangeRate:
		id_res = await self._get_currencies_ids(
			rate.base_currency.data, rate.target_currency.data
		)
		async with self._session_factory() as session:
			async with session.begin():
				try:
					res = await session.scalars(
						insert(ExRateORM)
						.values(
							base_crncy_id=id_res[rate.base_currency],
							target_crncy_id=id_res[rate.target_currency],
							value=rate.rate.value,
						)
						.returning(ExRateORM)
					)
				except sqlalchemy.exc.IntegrityError as e:
					raise ExchangeRateAlreadyExistsError(
						f"Exchange rate {rate.base_currency}-{rate.target_currency} "
						f"already exists"
					) from e

				return orm_ex_rate_to_dm_ex_rate(res.one())

	async def update_rate(self, rate: AlterExchangeRateDto) -> CurrenciesExchangeRate:
		id_res = await self._get_currencies_ids(
			rate.base_currency.data, rate.target_currency.data
		)
		async with self._session_factory() as session:
			async with session.begin():
				res = await session.scalars(
					update(ExRateORM)
					.where(
						ExRateORM.base_crncy_id == id_res[rate.base_currency],
						ExRateORM.target_crncy_id == id_res[rate.target_currency],
					)
					.values(value=rate.new_rate.value)
					.returning(ExRateORM)
				)
		try:
			return orm_ex_rate_to_dm_ex_rate(res.one())
		except NoResultFound:
			raise errors.ExchangeRateDoesntExistError(
				f"No exchange rate for {rate.base_currency}->{rate.target_currency}"
			)

	async def delete_rate(self, rate: DeleteExchangeRateDto) -> CurrenciesExchangeRate:
		id_res = await self._get_currencies_ids(
			rate.base_currency.data, rate.target_currency.data
		)
		async with self._session_factory() as session:
			async with session.begin():
				res = await session.scalars(
					delete(ExRateORM)
					.where(
						ExRateORM.base_crncy_id == id_res[rate.base_currency],
						ExRateORM.target_crncy_id == id_res[rate.target_currency],
					)
					.returning(ExRateORM)
				)
		try:
			return orm_ex_rate_to_dm_ex_rate(res.one())
		except NoResultFound:
			raise errors.ExchangeRateDoesntExistError(
				f"No exchange rate for {rate.base_currency}->{rate.target_currency}"
			)

	async def get_cross_rates(
		self, rate: GetExchangeRateDto
	) -> list[tuple[CurrenciesExchangeRate, CurrenciesExchangeRate]]:
		id_res = await self._get_currencies_ids(
			rate.base_currency.data, rate.target_currency.data
		)
		base_crncy_id = id_res[rate.base_currency]
		target_crncy_id = id_res[rate.target_currency]
		base_crncy_rates_cte = (
			select(ExRateORM)
			.where(
				or_(
					and_(
						ExRateORM.base_crncy_id == base_crncy_id,
						ExRateORM.target_crncy_id != target_crncy_id,
					),
					and_(
						ExRateORM.base_crncy_id != target_crncy_id,
						ExRateORM.target_crncy_id == base_crncy_id,
					),
				)
			)
			.cte()
		)
		target_crncy_rates_cte = (
			select(ExRateORM)
			.where(
				or_(
					and_(
						ExRateORM.base_crncy_id == target_crncy_id,
						ExRateORM.target_crncy_id != base_crncy_id,
					),
					and_(
						ExRateORM.base_crncy_id != base_crncy_id,
						ExRateORM.target_crncy_id == target_crncy_id,
					),
				)
			)
			.cte()
		)
		base_crncy_rates = aliased(ExRateORM, base_crncy_rates_cte)
		target_crncy_rates = aliased(ExRateORM, target_crncy_rates_cte)

		async with self._session_factory() as session:
			res = await session.execute(
				select(base_crncy_rates, target_crncy_rates).join_from(
					base_crncy_rates,
					target_crncy_rates,
					or_(
						base_crncy_rates.base_crncy_id
						== target_crncy_rates.base_crncy_id,
						base_crncy_rates.base_crncy_id
						== target_crncy_rates.target_crncy_id,
						base_crncy_rates.target_crncy_id
						== target_crncy_rates.base_crncy_id,
						base_crncy_rates.target_crncy_id
						== target_crncy_rates.target_crncy_id,
					),
				)
			)
		return [
			(orm_ex_rate_to_dm_ex_rate(rate1), orm_ex_rate_to_dm_ex_rate(rate2))
			for rate1, rate2 in res
		]

	async def _get_currencies_ids(
		self, *currencies: *Sequence[CurrencyCode]
	) -> dict[CurrencyCode, int]:
		async with self._session_factory() as session:
			id_res = await session.execute(
				select(CurrencyORM.id, CurrencyORM.code).where(
					CurrencyORM.code.in_(currencies)
				)
			)
		id_res = {code: id_ for id_, code in id_res}
		notfound = set(code for code in id_res).symmetric_difference(set(currencies))
		if notfound:
			raise errors.CurrencyDoesNotExistError(
				f"Currency(ies) with code(s) {', '.join(notfound)} not found"
			)

		return id_res
