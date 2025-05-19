import re
from collections import UserString
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator, ConfigDict, AliasPath, BeforeValidator

from currency_exchange.currency_exchange.domain.types import ExchangeRateValue

user_string_converter = BeforeValidator(lambda v: v.data if isinstance(v, UserString) else v)
exchange_rate_value_converter = BeforeValidator(lambda v: v.value if isinstance(v, ExchangeRateValue) else v)
CurrencyCodeField = Annotated[str, Field(pattern=re.compile('^[A-Z]{3}$')), user_string_converter]
CurrencyNameField = Annotated[str, Field(max_length=40), user_string_converter]
CurrencySignField = Annotated[str, Field(), user_string_converter]
ExchangeRateValueField = Annotated[
    float, Field(gt=0, allow_inf_nan=False), AfterValidator(lambda v: round(v, 2)), exchange_rate_value_converter
]


class CurrencyOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: CurrencyNameField
    code: CurrencyCodeField
    sign: CurrencySignField


class AddCurrencySchema(BaseModel):
    name: CurrencyNameField
    code: CurrencyCodeField
    sign: CurrencySignField


class UpdateCurrencySchema(BaseModel):
    new_name: Annotated[CurrencyNameField, Field(max_length=40, validation_alias='name')]
    new_sign: Annotated[CurrencySignField, Field(validation_alias='sign')]


class ExchangeRateOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baseCurrency: Annotated[CurrencyOutSchema, Field(validation_alias='base_currency')]
    targetCurrency: Annotated[CurrencyOutSchema, Field(validation_alias='target_currency')]
    rate: ExchangeRateValueField


class AddExchangeRateSchema(BaseModel):
    baseCurrencyCode: CurrencyCodeField
    targetCurrencyCode: CurrencyCodeField
    rate: ExchangeRateValueField


class UpdateExchangeRateSchema(BaseModel):
    rate: Annotated[float, Field(gt=0, allow_inf_nan=False), AfterValidator(lambda v: round(v, 6))]


class CurrencyConvertionDataSchema(BaseModel):
    from_: Annotated[str, Field(pattern=re.compile('[A-Z]{3}'))]
    to: CurrencyCodeField
    amount: Annotated[float, Field(gt=0, allow_inf_nan=False)]


class ConvertedCurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    baseCurrency: Annotated[CurrencyOutSchema, Field(validation_alias='base_currency')]
    targetCurrency: Annotated[CurrencyOutSchema, Field(validation_alias='target_currency')]
    rate: Annotated[ExchangeRateValueField, Field(validation_alias='exchange_rate')]
    amount: Annotated[
        float,
        Field(validation_alias=AliasPath('base_currency_amount', 'value')),
        AfterValidator(lambda v: round(v, 2))]
    convertedAmount: Annotated[
        float,
        Field(validation_alias=AliasPath('target_currency_amount', 'value')),
        AfterValidator(lambda v: round(v, 2))
    ]
