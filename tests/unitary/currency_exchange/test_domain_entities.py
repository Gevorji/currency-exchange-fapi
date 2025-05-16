import pytest

from currency_exchange.currency_exchange.domain.entities import Currency, CurrenciesExchangeRate
from currency_exchange.currency_exchange.domain.types import (CurrencyCode, CurrencyAmount,
                                                              CurrencySign, CurrencyName, ExchangeRateValue)
from currency_exchange.currency_exchange.domain import errors


@pytest.mark.parametrize(
    'code,name,sign', [
        ['', 'some name', '$'], ['USD', '', '$'], ['USD', 'some name', ''],
        ['USDD', 'some sign', '$'], ['US1', 'some sign', '$'], ['US', 'some sign', '$'],
        ['ЮСД', 'some sign', '$'], ['USDD', 'some_sign', '$'], ['USDD', 'sign.', '$']
    ]
)
def test_currency_init_error(code, name, sign):
    with pytest.raises(errors.CurrencyCoreError):
        Currency(CurrencyCode(code), CurrencySign(sign), CurrencyName(name))


@pytest.mark.parametrize('rate', [0, -1, float('inf'), float('-inf')])
def test_exchange_rate_incorrect_rate_value_error(rate):
    with pytest.raises(errors.IncorrectExchangeRateValue):
        CurrenciesExchangeRate(
            Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
            Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
            ExchangeRateValue(rate)
        )


def test_exchange_rate_init_with_amount_successful():
    er = CurrenciesExchangeRate(
        Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
        Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
        ExchangeRateValue(1000), CurrencyAmount(10)
    )
    assert er.rate.value == 100


@pytest.mark.parametrize('amount', [0, -1, float('inf'), float('-inf')])
def test_exchange_rate_incorrect_amount_value_error(amount):
    with pytest.raises(errors.IncorrectCurrencyAmount):
        CurrenciesExchangeRate(
            Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
            Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
            ExchangeRateValue(5), CurrencyAmount(amount)
        )


def test_exchange_rate_convertion_successful():
    rate = 90
    convert_amount = 5
    er = CurrenciesExchangeRate(
            Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
            Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
            ExchangeRateValue(rate)
        )

    assert er.convert(CurrencyAmount(convert_amount)) == rate * convert_amount


@pytest.mark.parametrize('convert_amount', [0, -1, float('inf'), float('-inf')])
def test_exchange_rate_convertion_error_on_incorrect_amount(convert_amount):
    rate = 90
    er = CurrenciesExchangeRate(
        Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
        Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
        ExchangeRateValue(rate)
    )

    with pytest.raises(errors.IncorrectCurrencyAmount):
        er.convert(CurrencyAmount(convert_amount))


@pytest.mark.parametrize(
    'rate1,rate2',
    [
       [
           CurrenciesExchangeRate(
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
               ExchangeRateValue(0.01)
           ),
           CurrenciesExchangeRate(
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               Currency(CurrencyCode('EUR'), CurrencySign('E'), CurrencyName('Euro')),
               ExchangeRateValue(0.88)
           ),
       ],
       [
           CurrenciesExchangeRate(
               Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               ExchangeRateValue(100)
           ),
           CurrenciesExchangeRate(
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               Currency(CurrencyCode('EUR'), CurrencySign('E'), CurrencyName('Euro')),
               ExchangeRateValue(0.88)
           ),
       ],
       [
           CurrenciesExchangeRate(
               Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               ExchangeRateValue(100)
           ),
           CurrenciesExchangeRate(
               Currency(CurrencyCode('EUR'), CurrencySign('E'), CurrencyName('Euro')),
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               ExchangeRateValue(1/0.88)
           ),
       ],
       [
           CurrenciesExchangeRate(
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
               ExchangeRateValue(0.01)
           ),
           CurrenciesExchangeRate(
               Currency(CurrencyCode('EUR'), CurrencySign('E'), CurrencyName('Euro')),
               Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
               ExchangeRateValue(1/0.88)
           ),
       ],
    ]
)
def test_exchange_rate_get_cross_rate_successful(rate1, rate2):
    cross_rate = rate1.get_cross_rate(rate2)

    assert cross_rate.base.code == 'RUB'
    assert cross_rate.target.code == 'EUR'
    assert cross_rate.rate.value == pytest.approx(100/(1/0.88))


def test_exchange_rate_get_cross_rate_error_when_no_common_currency():
    rate1 = CurrenciesExchangeRate(
        Currency(CurrencyCode('RUB'), CurrencySign('Р'), CurrencyName('Russian ruble')),
        Currency(CurrencyCode('USD'), CurrencySign('$'), CurrencyName('US dollar')),
        ExchangeRateValue(100)
    )
    rate2 = CurrenciesExchangeRate(
        Currency(CurrencyCode('AUD'), CurrencySign('$'), CurrencyName('US dollar')),
        Currency(CurrencyCode('EUR'), CurrencySign('E'), CurrencyName('Euro')),
        ExchangeRateValue(0.88)
    )

    with pytest.raises(errors.CrossExchangeRateComputationError):
        rate1.get_cross_rate(rate2)