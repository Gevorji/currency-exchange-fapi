import pytest

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.testing.provision import follower_url_from_main

import currency_exchange.db.session
from currency_exchange.auth.schemas import UserDbOut
from currency_exchange.auth.providers import jwt_revocation_checker_provider, JWTIssuerProvider
from currency_exchange.auth.dbmodels import User, UserCategory
from currency_exchange.currency_exchange.fapiadoption.routes.currencies import currencies_router
from currency_exchange.currency_exchange.fapiadoption.routes.exchangerates import exchange_rates_router
from currency_exchange.currency_exchange.fapiadoption.routes.currenciesconvertion import currencies_convertion_router
from currency_exchange.currency_exchange.fapiadoption.appadapter import currency_exchange_app
from currency_exchange.currency_exchange.fapiadoption.main import app as fapi_app
from currency_exchange.currency_exchange.infrastructure.db.dbmodels import (CurrencyORMModel,
                                                                            CurrenciesExchangeRateORMModel)
from .utils import get_currency_from_db, get_exchange_rate_from_db

pytestmark = pytest.mark.anyio

@pytest.fixture(scope="module")
async def app(local_sessionmaker):
    global fapi_app
    def jwt_token_revocation_checker_stub():
        async def check_revocation(*args, **kwargs):
            return False
        return check_revocation

    currency_exchange.db.session.async_session_factory = local_sessionmaker
    currency_exchange_app._exchange_rates_repo._session_factory = local_sessionmaker
    currency_exchange_app._currencies_repo._session_factory = local_sessionmaker

    fapi_app.dependency_overrides = {jwt_revocation_checker_provider: jwt_token_revocation_checker_stub}
    return fapi_app


@pytest.fixture(scope="module", autouse=True)
async def app_user(local_sessionmaker):
    session = local_sessionmaker()
    user = User(username='ce_client', password='abrakadabra', category=UserCategory.API_CLIENT)
    async with session.begin():
        session.add(user)
    session.close()
    return user


@pytest.fixture(scope="module", autouse=True)
async def admin_user(local_sessionmaker):
    session = local_sessionmaker()
    user = User(username='ce_admin', password='abrakadabra', category=UserCategory.ADMIN)
    async with session.begin():
        session.add(user)
    session.close()
    return user


@pytest.fixture(scope="module")
async def access_token(app_user):
    issuer = JWTIssuerProvider(UserDbOut.model_validate(app_user), 'none')
    return issuer.get_access_token()


@pytest.fixture(scope="module")
async def admin_access_token(admin_user):
    issuer = JWTIssuerProvider(admin_user, 'none')
    return issuer.get_access_token()


class TestCurrenciesEndpoints:
    all_currencies_endpoint = '/currencies'
    add_currency_endpoint = '/currencies'

    @pytest.fixture(scope='class')
    async def get_currency_request_endpoint(self):
        def _get_currency_request_endpoint(code: str):
            return f'/currency/{code}'
        return _get_currency_request_endpoint

    async def test_get_all_currencies_successful(self, access_token, request_client, db_session):
        response = await request_client.get(self.all_currencies_endpoint,
                                      headers={'Authorization': f'Bearer {access_token[0]}'})

        assert response.status_code == 200

        response_data = response.json()
        currencies_from_db = await db_session.scalars(select(CurrencyORMModel))
        currencies_from_db = currencies_from_db.all()

        assert len(response_data) == len(currencies_from_db)

    async def test_get_currency_successful(self, access_token, request_client, db_session,
                                           get_currency_request_endpoint):
        response = await request_client.get(get_currency_request_endpoint('USD'),
                                            headers={'Authorization': f'Bearer {access_token[0]}'})

        assert response.status_code == 200
        response_data = response.json()
        usd_from_db = await get_currency_from_db('USD', db_session)

        assert response_data['id'] == usd_from_db.id
        assert response_data['code'] == 'USD'

    async def test_get_currency_error_when_currency_doesnt_exist(self, access_token, request_client,
                                                                 get_currency_request_endpoint):
        response = await request_client.get(get_currency_request_endpoint('XXX'),
                                            headers={'Authorization': f'Bearer {access_token[0]}'})
        assert response.status_code == 404

    async def test_get_currency_error_when_currency_code_not_present_in_url(self, access_token, request_client,
                                                                            get_currency_request_endpoint):
        response = await request_client.get(get_currency_request_endpoint(''),
                                            headers={'Authorization': f'Bearer {access_token[0]}'},
                                            follow_redirects=True)
        assert response.status_code == 400


    async def test_get_currency_error_when_currency_code_is_invalid(self, access_token, request_client,
                                                                    get_currency_request_endpoint):
        response = await request_client.get(get_currency_request_endpoint('US'),
                                            headers={'Authorization': f'Bearer {access_token[0]}'})
        assert response.status_code == 400

    async def test_update_currency_successful(self, access_token, request_client, get_currency_request_endpoint):
        new_name = 'Dirty bucks'
        new_sign = 'X'
        response = await request_client.patch(get_currency_request_endpoint('USD'),
                                               headers= {'Authorization': f'Bearer {access_token[0]}'},
                                               data={'name': new_name, 'sign': new_sign})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['name'] == new_name
        assert response_data['sign'] == new_sign

    async def test_update_currency_error_when_currency_doesnt_exist(self, access_token, request_client,
                                                                    get_currency_request_endpoint):
        response = await request_client.patch(get_currency_request_endpoint('XXX'),
                                              headers={'Authorization': f'Bearer {access_token[0]}'},
                                              data={'name': 'X', 'sign': 'x'})
        assert response.status_code == 404

    @pytest.mark.parametrize(
        'data', [
            {'code': 'X', 'name': 'X', 'sign': 'X'}, {'code': 'USD', 'name': None, 'sign': None},
            {'code': '', 'name': 'X', 'sign': 'X'}, {'code': 'USD', 'nme': 'X', 'sgn': 'X'},
        ]
    )
    async def test_update_currency_error_when_bad_data_in_request(self, data, access_token, request_client,
                                                                    get_currency_request_endpoint):
        response = await request_client.patch(get_currency_request_endpoint(data['code']),
                                              headers={'Authorization': f'Bearer {access_token[0]}'},
                                              data={k: v for k,v in data.items() if k != 'code' and v},
                                              follow_redirects=True)
        assert response.status_code == 400

    async def test_add_currency_successful(self, access_token, request_client, db_session):
        code, name, sign = 'AMD', 'Dram', 'X'
        response = await request_client.post(self.add_currency_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={'code': code, 'name': name, 'sign': sign})

        assert response.status_code == 201

        response_data = response.json()
        currency_from_db = await get_currency_from_db(code, db_session)
        assert response_data['id'] == currency_from_db.id
        assert response_data['name'] == currency_from_db.name
        assert response_data['sign'] == currency_from_db.sign

    async def test_add_currency_error_when_currency_already_exists(self, access_token, request_client):
        response = await request_client.post(self.add_currency_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={'code': 'USD', 'name': 'X', 'sign': 'X'})
        assert response.status_code == 409

    @pytest.mark.parametrize(
        'data', [
            {'code': 'AF', 'name': 'X', 'sign': 'X'}, {'code': 'USD', 'name': None, 'sign': 'X'},
            {'code': 'USD', 'name': 'X', 'sign': None}, {'code': 'USD', 'nae': 'X', 'sgn': 'X'},
        ]
    )
    async def test_add_currency_error_when_bad_data_in_request(self, data, access_token, request_client):
        response = await request_client.post(self.add_currency_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={k: v for k, v in data.items() if v})
        assert response.status_code == 400

    async def test_delete_currency_successful(self, admin_access_token, request_client, db_session,
                                              get_currency_request_endpoint):
        response = await request_client.delete(get_currency_request_endpoint('USD'),
                                               headers={'Authorization': f'Bearer {admin_access_token[0]}'})

        assert response.status_code == 200
        assert await get_currency_from_db('USD', db_session) is None

    async def test_delete_currency_error_when_currency_doesnt_exist(self, admin_access_token, request_client,
                                                                    get_currency_request_endpoint):
        response = await request_client.delete(get_currency_request_endpoint('XXX'),
                                               headers={'Authorization': f'Bearer {admin_access_token[0]}'})

        assert response.status_code == 404

    @pytest.mark.parametrize('code', ['US', ''])
    async def test_delete_currency_error_when_bad_data_in_request(self, code, admin_access_token, request_client,
                                                                  get_currency_request_endpoint):
        response = await request_client.delete(get_currency_request_endpoint(code),
                                               headers={'Authorization': f'Bearer {admin_access_token[0]}'},
                                               follow_redirects=True)
        assert response.status_code == 400


class TestExchangeRatesEndpoints:
    get_all_exch_rates_endpoint = '/exchangerates'
    add_exch_rate_endpoint = '/exchangerates'

    @pytest.fixture(scope='class')
    async def get_exchange_rate_request_endpoint(self):
        def _get_exchange_rate_request_endpoint(codes: str):
            return f'/exchangerate/{codes}'
        return _get_exchange_rate_request_endpoint

    async def test_get_all_exchange_rates(self, access_token, request_client, db_session):
        response = await request_client.get(self.get_all_exch_rates_endpoint,
                                      headers={'Authorization': f'Bearer {access_token[0]}'})

        assert response.status_code == 200

        response_data = response.json()
        ers_from_db = await db_session.scalars(select(CurrenciesExchangeRateORMModel))
        ers_from_db = ers_from_db.all()

        assert len(response_data) == len(ers_from_db)

    async def test_get_exchange_rate_successful(self, access_token, request_client,
                                                get_exchange_rate_request_endpoint, db_session):
        response = await request_client.get(get_exchange_rate_request_endpoint('EURUSD'),
                                      headers={'Authorization': f'Bearer {access_token[0]}'})

        assert response.status_code == 200

        response_data = response.json()
        er_from_db = await get_exchange_rate_from_db('EUR', 'USD', db_session)
        assert response_data['id'] == er_from_db.id

    async def test_get_exchange_rate_error_when_exchange_rate_doesnt_exist(self, access_token, request_client,
                                                                           get_exchange_rate_request_endpoint):
        response = await request_client.get(get_exchange_rate_request_endpoint('EURRUB'),
                                     headers={'Authorization': f'Bearer {access_token[0]}'})

        assert response.status_code == 404

    @pytest.mark.parametrize('codes', ['EUR', 'EURUS', ''])
    async def test_get_exchange_rate_error_when_bad_data_in_request(self, codes, access_token, request_client,
                                                                    get_exchange_rate_request_endpoint):
        response = await request_client.get(get_exchange_rate_request_endpoint(codes),
                                      headers={'Authorization': f'Bearer {access_token[0]}'}, follow_redirects=True)

        assert response.status_code == 400

    async def test_update_exchange_rate_successful(self, access_token, request_client, db_session,
                                                   get_exchange_rate_request_endpoint):
        new_rate = 80
        response = await request_client.patch(get_exchange_rate_request_endpoint('RUBUSD'),
                                        headers={'Authorization': f'Bearer {access_token[0]}'},
                                        data={'rate': new_rate})

        assert response.status_code == 200

        er_from_db = await get_exchange_rate_from_db('RUB', 'USD', db_session)
        assert new_rate == er_from_db.value.value

    async def test_update_exchange_rate_error_when_rate_doesnt_exist(self, access_token, request_client,
                                                                       get_exchange_rate_request_endpoint):
        new_rate = 80
        response = await request_client.patch(get_exchange_rate_request_endpoint('XXXYYY'),
                                        headers={'Authorization': f'Bearer {access_token[0]}'},
                                        data={'rate': new_rate})

        assert response.status_code == 404

    @pytest.mark.parametrize(
        'data', [
            {'codes': 'EURUSD', 'rate': 0}, {'codes': 'EURUSD', 'rate': -1}, {'codes': 'EURUSD', 'rate': None},
            {'codes': 'EURUSD', 'rat': 10}, {'codes': 'EUR', 'rate': 10}, {'codes': 'EURUS', 'rate': 10},
            {'codes': '', 'rate': 10},
        ]
    )
    async def test_update_exchange_rate_error_when_bad_data_in_request(self, data, access_token, request_client,
                                                                       get_exchange_rate_request_endpoint):
        response = await request_client.patch(get_exchange_rate_request_endpoint(data['codes']),
                                        headers={'Authorization': f'Bearer {access_token[0]}'},
                                        data={k: v for k, v in data.items() if k != 'codes' and v},
                                        follow_redirects=True)

        assert response.status_code == 400

    async def test_add_exchange_rate_successful(self, access_token, request_client, db_session):
        rate = 1.15
        response = await request_client.post(self.add_exch_rate_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={'baseCurrencyCode': 'DKK',
                                                   'targetCurrencyCode': 'USD', 'rate': rate})

        assert response.status_code == 201

        er_from_db = await get_exchange_rate_from_db('DKK', 'USD', db_session)
        assert er_from_db.base_crncy.code == 'DKK'
        assert er_from_db.target_crncy.code == 'USD'
        assert er_from_db.value.value == pytest.approx(rate)

    async def test_add_exchange_rate_error_when_rate_already_exists(self, access_token, request_client):
        response = await request_client.post(self.add_exch_rate_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={'baseCurrencyCode': 'EUR', 'targetCurrencyCode': 'USD', 'rate': 1})
        assert response.status_code == 409

    @pytest.mark.parametrize(
        'data', [
            {'baseCurrencyCode': 'EUR', 'targetCurrencyCode': 'USD', 'rate': 0},
            {'baseCurrencyCode': 'EUR', 'targetCurrencyCode': 'USD', 'rate': -1},
            {'baseCurrencyCode': 'EU', 'target': 'USD', 'targetCurrencyCode': 1},
            {'baseCurrencyCode': 'EUR', 'targetCurrencyCode': 'US', 'rate': 1},
            {'baseCurrencyCode': None, 'targetCurrencyCode': 'USD', 'rate': 1},
            {'baseCurrencyCode': None, 'targetCurrencyCode': None, 'rate': 1},
            {'baseurrencyCode': 'EUR', 'targetCurrncyCode': 'USD', 'rate': 1},
        ]
    )
    async def test_add_exchange_rate_error_when_bad_data_in_request(self, data, access_token, request_client):
        response = await request_client.post(self.add_exch_rate_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={k: v for k, v in data.items() if v is not None})
        assert response.status_code == 400

    async def test_add_exchange_rate_error_when_currency_doesnt_exist(self, access_token, request_client):
        response = await request_client.post(self.add_exch_rate_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             data={'baseCurrencyCode': 'XXX', 'targetCurrencyCode': 'USD', 'rate': 1})
        assert response.status_code == 404

    async def test_delete_exchange_rate_successful(self, admin_access_token, request_client, db_session,
                                                   get_exchange_rate_request_endpoint):
        response = await request_client.delete(get_exchange_rate_request_endpoint('EURUSD'),
                                         headers={'Authorization': f'Bearer {admin_access_token[0]}'})

        assert response.status_code == 200

        assert await get_exchange_rate_from_db('EUR', 'USD', db_session) is None

    async def test_delete_exchange_rate_error_when_rate_doesnt_exist(self, admin_access_token, request_client,
                                                                     get_exchange_rate_request_endpoint):
        response = await request_client.delete(get_exchange_rate_request_endpoint('XXXYYY'),
                                         headers={'Authorization': f'Bearer {admin_access_token[0]}'})

        assert response.status_code == 404


class TestConvertionEndpoint:
    convertion_endpoint = '/exchange'

    async def test_convert_currency_straight_strat_successful(self, access_token, request_client, db_session):
        amount = 1000
        response = await request_client.get(self.convertion_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             params={'from': 'RUB', 'to': 'USD', 'amount': amount})
        assert response.status_code == 200

        er = await get_exchange_rate_from_db('RUB', 'USD', db_session)
        response_data = response.json()
        assert response_data['convertedAmount'] == pytest.approx(er.value.value * amount)

    async def test_convert_currency_reversed_strat_successful(self, access_token, request_client, db_session):
        amount = 100
        response = await request_client.get(self.convertion_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             params={'from': 'USD', 'to': 'RUB', 'amount': amount})
        assert response.status_code == 200

        er = await get_exchange_rate_from_db('RUB', 'USD', db_session)
        response_data = response.json()
        assert response_data['convertedAmount'] == pytest.approx(1/er.value.value * amount)

    async def test_convert_currency_cross_rate_strat_successful(self, access_token, request_client, db_session):
        amount = 100
        response = await request_client.get(self.convertion_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             params={'from': 'EUR', 'to': 'RUB', 'amount': amount})
        assert response.status_code == 200

        er1 = await get_exchange_rate_from_db('EUR', 'USD', db_session)
        er2 = await get_exchange_rate_from_db('RUB', 'USD', db_session)
        response_data = response.json()
        assert response_data['convertedAmount'] == pytest.approx(er1.value.value/er2.value.value * amount)


    async def test_convert_currency_error_when_rate_doesnt_exist(self, access_token, request_client):
        response = await request_client.get(self.convertion_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             params={'from': 'GBP', 'to': 'KZT', 'amount': 100})

        assert response.status_code == 404

    @pytest.mark.parametrize(
        'data', [
            {'from': 'US', 'to': 'EUR', 'amount': 1000}, {'from': 'USD', 'to': 'EUR', 'amount': 0},
            {'from': 'USD', 'to': 'EUR', 'amount': -1}, {'from': None, 'to': 'EUR', 'amount': 1000},
            {'frm': 'USD', 'to': 'EUR', 'amount': 1000}, {'from': None, 'to': 'EUR', 'more': 'yes', 'amount': 1000}
        ]
    )
    async def test_convert_currency_error_when_bad_data_in_request(self, data, access_token, request_client):
        response = await request_client.get(self.convertion_endpoint,
                                             headers={'Authorization': f'Bearer {access_token[0]}'},
                                             params={'from': 'GBP', 'to': 'KZT', 'amount': 100})

        assert response.status_code == 404
