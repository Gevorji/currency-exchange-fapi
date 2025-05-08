import pytest

from currency_exchange.currency_exchange.application.dto import (GetCurrencyDto, AddCurrencyDto,
                                                                 AlterCurrencyDto, DeleteCurrencyDto, ExchangeRateDto,
                                                                 GetExchangeRateDto, AddExchangeRateDto,
                                                                 AlterExchangeRateDto, DeleteExchangeRateDto)
from currency_exchange.currency_exchange.domain.entities import Currency

from currency_exchange.currency_exchange.domain.types import CurrencyCode, CurrencySign, CurrencyName, ExchangeRateValue
from currency_exchange.currency_exchange.application import errors
from currency_exchange.currency_exchange.domain.entities import CurrenciesExchangeRate
from .utils import get_currency_from_db, get_exchange_rate_from_db

pytestmark = pytest.mark.anyio


class TestCurrenciesRepo:

    async def test_get_all_currencies(self, currencies_repo):
        res = await currencies_repo.get_all_currencies()
        assert all(isinstance(c, Currency) for c in res)

    async def test_get_currency_success(self, currencies_repo):
        res = await currencies_repo.get_currency(GetCurrencyDto(CurrencyCode('USD')))
        assert res.code == 'USD'

        res = await currencies_repo.get_currency(GetCurrencyDto(name=CurrencyName('Euro')))
        assert res.code == 'EUR'

    async def test_get_currency_error_when_currency_doesnt_exist(self, currencies_repo):
        with pytest.raises(errors.CurrencyDoesNotExistError):
            await currencies_repo.get_currency(GetCurrencyDto(CurrencyCode('XXX')))

    async def test_add_currency_successful(self, currencies_repo):
        res = await currencies_repo.save_currency(
            AddCurrencyDto(CurrencyCode('AUD'), CurrencyName('Australian dollar'), CurrencySign('A'))
        )

        assert res.id is not None

    async def test_add_currency_error_when_currency_already_exists(self, currencies_repo):
        with pytest.raises(errors.CurrencyAlreadyExistsError):
            await currencies_repo.save_currency(
                AddCurrencyDto(CurrencyCode('USD'), CurrencyName('US Dollar'), CurrencySign('$'))
            )


    async def test_update_currency_successful(self, currencies_repo, local_sessionmaker):
        new_name = CurrencyName('Russian dollar')
        await currencies_repo.update_currency(AlterCurrencyDto(CurrencyCode('RUB'), new_name))
        new_currency_model = await get_currency_from_db('RUB', local_sessionmaker())
        assert new_currency_model.name == new_name

        new_sign = CurrencySign('D')
        await currencies_repo.update_currency(AlterCurrencyDto(CurrencyCode('USD'), new_sign=new_sign))
        new_currency_model = await get_currency_from_db('USD', local_sessionmaker())
        assert new_currency_model.sign == new_sign

    async def test_update_currency_error_when_currency_does_not_exist(self, currencies_repo):
        with pytest.raises(errors.CurrencyDoesNotExistError):
            await currencies_repo.update_currency(AlterCurrencyDto(CurrencyCode('XXX'), new_sign=CurrencySign('D')))

    async def test_delete_currency_successful(self, currencies_repo, local_sessionmaker):
        await currencies_repo.delete_currency(DeleteCurrencyDto(code=CurrencyCode('USD')))
        assert await get_currency_from_db('USD', local_sessionmaker()) is None

    async def test_delete_currency_error_when_currency_doesnt_exist(self, currencies_repo):
        with pytest.raises(errors.CurrencyDoesNotExistError):
            await currencies_repo.delete_currency(DeleteCurrencyDto(code=CurrencyCode('XXX')))


class TestExchangeRatesRepo:

    async def test_get_all_exchange_rates(self, exchange_rates_repo):
        res = await exchange_rates_repo.get_all_rates()
        assert all(isinstance(er, CurrenciesExchangeRate) for er in res)

    async def test_get_exchange_rate_success(self, exchange_rates_repo):
        res = await exchange_rates_repo.get_rate(GetExchangeRateDto(CurrencyCode('RUB'), CurrencyCode('USD')))
        assert res.base.code == 'RUB'
        assert res.target.code == 'USD'

    async def test_get_exchange_rate_error_when_rate_doesnt_exist(self, exchange_rates_repo):
        with pytest.raises(errors.ExchangeRateDoesntExistError):
            await exchange_rates_repo.get_rate(GetExchangeRateDto(CurrencyCode('AAA'), CurrencyCode('DDD')))

    async def test_add_exchange_rate_successful(self, exchange_rates_repo, local_sessionmaker):
        await exchange_rates_repo.save_rate(AddExchangeRateDto(CurrencyCode('JPY'), CurrencyCode('DKK'),
                                                                     ExchangeRateValue(11.1)))
        new_er_model = await get_exchange_rate_from_db('JPY', 'DKK', local_sessionmaker())
        assert new_er_model.id is not None

    async def test_add_exchange_rate_error_when_rate_already_exists(self, exchange_rates_repo):
        with pytest.raises(errors.ExchangeRateAlreadyExistsError):
            await exchange_rates_repo.save_rate(AddExchangeRateDto(CurrencyCode('RUB'), CurrencyCode('USD'),
                                                                   ExchangeRateValue(11.1)))

    async def test_add_exchange_rate_error_when_currency_doesnt_exist(self, exchange_rates_repo):
        with pytest.raises(errors.CurrencyDoesNotExistError):
            await exchange_rates_repo.save_rate(AddExchangeRateDto(CurrencyCode('XXX'), CurrencyCode('USD'),
                                                                   ExchangeRateValue(11.1)))

    async def test_update_rate_successful(self, exchange_rates_repo, local_sessionmaker):
        new_rate = ExchangeRateValue(1/98)
        await exchange_rates_repo.update_rate(
            AlterExchangeRateDto(CurrencyCode('RUB'), CurrencyCode('USD'), new_rate)
        )
        new_er_model = await get_exchange_rate_from_db('RUB', 'USD', local_sessionmaker())

        assert new_er_model.base_crncy.code == 'RUB'
        assert new_er_model.target_crncy.code == 'USD'
        assert new_er_model.value.value == pytest.approx(new_rate.value)

    async def test_update_rate_error_when_exchange_rate_doesnt_exist(self, exchange_rates_repo):
        with pytest.raises(errors.ExchangeRateDoesntExistError):
            await exchange_rates_repo.update_rate(
            AlterExchangeRateDto(CurrencyCode('USD'), CurrencyCode('RUB'), ExchangeRateValue(11.1))
            )

    async def test_delete_exchange_rate_successful(self, exchange_rates_repo, local_sessionmaker):
        await exchange_rates_repo.delete_rate(
            DeleteExchangeRateDto(CurrencyCode('RUB'), CurrencyCode('USD'))
        )

        assert await get_exchange_rate_from_db('RUB', 'USD', local_sessionmaker()) is None

    async def test_delete_exchange_rate_error_when_rate_doesnt_exist(self, exchange_rates_repo):
        with pytest.raises(errors.ExchangeRateDoesntExistError):
            await exchange_rates_repo.delete_rate(
                DeleteExchangeRateDto(CurrencyCode('USD'), CurrencyCode('RUB'))
            )

    async def test_get_cross_rates_successful(self, exchange_rates_repo):
        cross_rates = await exchange_rates_repo.get_cross_rates(
            GetExchangeRateDto(CurrencyCode('RUB'), CurrencyCode('EUR')),
        )

        # (RUB-USD, USD-EUR), (RUB-USD, EUR-USD), (EUR-JPY, RUB-JPY), (DKK-EUR, RUB-DKK)
        assert len(cross_rates) == 4

        res_currency_codes_tuples = {((er1.base.code.data, er1.target.code.data),
                                      (er2.base.code.data, er2.target.code.data)) for er1, er2 in cross_rates}

        correct_currency_codes_tuples = [(('RUB', 'USD'), ('USD', 'EUR')), (('RUB', 'USD'), ('EUR', 'USD')),
                                         (('EUR', 'JPY'), ('RUB', 'JPY')), (('DKK', 'EUR'), ('RUB', 'DKK'))]

        assert all(currency_codes in res_currency_codes_tuples or currency_codes[::-1] in res_currency_codes_tuples
                   for currency_codes in correct_currency_codes_tuples)