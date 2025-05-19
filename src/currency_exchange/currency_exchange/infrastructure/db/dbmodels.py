from sqlalchemy import String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from currency_exchange.config import SQLAModelBase
from currency_exchange.utils.importobject import import_object
from ...domain.types import CurrencyCode, CurrencySign, CurrencyName, ExchangeRateValue

BaseModel = import_object(SQLAModelBase)


class CurrencyORMModel(BaseModel):
	__tablename__ = "currency"

	id: Mapped[int] = mapped_column(primary_key=True)
	code: Mapped[CurrencyCode] = mapped_column(String(3), unique=True)
	sign: Mapped[CurrencySign] = mapped_column(String)
	name: Mapped[CurrencyName] = mapped_column(String)


class CurrenciesExchangeRateORMModel(BaseModel):
	__tablename__ = "exchange_rate"
	__table_args__ = (UniqueConstraint("base_crncy_id", "target_crncy_id"),)

	id: Mapped[int] = mapped_column(primary_key=True)
	base_crncy_id: Mapped[int] = mapped_column(
		ForeignKey("currency.id", ondelete="CASCADE")
	)
	target_crncy_id: Mapped[int] = mapped_column(
		ForeignKey("currency.id", ondelete="CASCADE")
	)
	base_crncy: Mapped["CurrencyORMModel"] = relationship(
		primaryjoin="CurrenciesExchangeRateORMModel.base_crncy_id==CurrencyORMModel.id",
		lazy="selectin",
	)
	target_crncy: Mapped["CurrencyORMModel"] = relationship(
		primaryjoin="CurrenciesExchangeRateORMModel.target_crncy_id==CurrencyORMModel.id",
		lazy="selectin",
	)
	_value: Mapped[float] = mapped_column(Float(precision=6))

	@hybrid_property
	def value(self):
		return ExchangeRateValue(self._value)

	@value.setter
	def value(self, value: ExchangeRateValue):
		self._value = value.value

	@value.expression
	def value(cls):
		return cls._value
