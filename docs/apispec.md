---
title: FastAPI v0.1.0
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="fastapi">FastAPI v0.1.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

# Authentication

- oAuth2 authentication. 

    - Flow: password

    - Token URL = [/tokens/gain](/tokens/gain)

|Scope|Scope Description|
|---|---|

- HTTP Authentication, scheme: basic 

<h1 id="fastapi-currency-exchange">Currency exchange</h1>

## Currency exchange-get_all_currencies

<a id="opIdCurrency exchange-get_all_currencies"></a>

`GET /currencies`

*Get All Currencies*

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  }
]
```

<h3 id="currency-exchange-get_all_currencies-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="currency-exchange-get_all_currencies-responseschema">Response Schema</h3>

Status Code **200**

*Response Currency Exchange-Get All Currencies*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response Currency Exchange-Get All Currencies|[[CurrencyOutSchema](#schemacurrencyoutschema)]|false|none|none|
|» CurrencyOutSchema|[CurrencyOutSchema](#schemacurrencyoutschema)|false|none|none|
|»» id|integer|true|none|none|
|»» name|string|true|none|none|
|»» code|string|true|none|none|
|»» sign|string|true|none|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: currency:request )
</aside>

## Currency exchange-add_currency

<a id="opIdCurrency exchange-add_currency"></a>

`POST /currencies`

*Add Currency*

> Body parameter

```yaml
name: string
code: string
sign: string

```

<h3 id="currency-exchange-add_currency-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AddCurrencySchema](#schemaaddcurrencyschema)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "name": "string",
  "code": "string",
  "sign": "string"
}
```

<h3 id="currency-exchange-add_currency-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[CurrencyOutSchema](#schemacurrencyoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Not enough fields provided|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Currency with such code already exists|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: currency:create ), OAuth2PasswordBearer
</aside>

## Currency exchange-get_currency

<a id="opIdCurrency exchange-get_currency"></a>

`GET /currency/{currency_code}`

*Get Currency*

<h3 id="currency-exchange-get_currency-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|currency_code|path|string|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "name": "string",
  "code": "string",
  "sign": "string"
}
```

<h3 id="currency-exchange-get_currency-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[CurrencyOutSchema](#schemacurrencyoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Currency code not provided|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: currency:request ), OAuth2PasswordBearer
</aside>

## Currency exchange-update_currency

<a id="opIdCurrency exchange-update_currency"></a>

`PATCH /currency/{currency_code}`

*Update Currency*

> Body parameter

```yaml
name: string
sign: string

```

<h3 id="currency-exchange-update_currency-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|currency_code|path|string|true|none|
|body|body|[UpdateCurrencySchema](#schemaupdatecurrencyschema)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "name": "string",
  "code": "string",
  "sign": "string"
}
```

<h3 id="currency-exchange-update_currency-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[CurrencyOutSchema](#schemacurrencyoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request data|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: currency:update ), OAuth2PasswordBearer
</aside>

## Currency exchange-delete_currency

<a id="opIdCurrency exchange-delete_currency"></a>

`DELETE /currency/{currency_code}`

*Delete Currency*

<h3 id="currency-exchange-delete_currency-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|currency_code|path|string|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="currency-exchange-delete_currency-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request data|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="currency-exchange-delete_currency-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all ), OAuth2PasswordBearer
</aside>

## Currency exchange-get_all_exchange_rates

<a id="opIdCurrency exchange-get_all_exchange_rates"></a>

`GET /exchangerates`

*Get All Exchange Rates*

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "baseCurrency": {
      "id": 0,
      "name": "string",
      "code": "string",
      "sign": "string"
    },
    "targetCurrency": {
      "id": 0,
      "name": "string",
      "code": "string",
      "sign": "string"
    },
    "rate": 0
  }
]
```

<h3 id="currency-exchange-get_all_exchange_rates-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="currency-exchange-get_all_exchange_rates-responseschema">Response Schema</h3>

Status Code **200**

*Response Currency Exchange-Get All Exchange Rates*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response Currency Exchange-Get All Exchange Rates|[[ExchangeRateOutSchema](#schemaexchangerateoutschema)]|false|none|none|
|» ExchangeRateOutSchema|[ExchangeRateOutSchema](#schemaexchangerateoutschema)|false|none|none|
|»» id|integer|true|none|none|
|»» baseCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|»»» id|integer|true|none|none|
|»»» name|string|true|none|none|
|»»» code|string|true|none|none|
|»»» sign|string|true|none|none|
|»» targetCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|»» rate|number|true|none|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: exch_rate:request )
</aside>

## Currency exchange-add_exchange_rate

<a id="opIdCurrency exchange-add_exchange_rate"></a>

`POST /exchangerates`

*Add Exchange Rate*

> Body parameter

```yaml
baseCurrencyCode: string
targetCurrencyCode: string
rate: 0

```

<h3 id="currency-exchange-add_exchange_rate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[AddExchangeRateSchema](#schemaaddexchangerateschema)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0
}
```

<h3 id="currency-exchange-add_exchange_rate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[ExchangeRateOutSchema](#schemaexchangerateoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad data in request|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency(ies) not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Exchange rate already exists|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: exch_rate:create ), OAuth2PasswordBearer
</aside>

## Currency exchange-get_exchange_rate

<a id="opIdCurrency exchange-get_exchange_rate"></a>

`GET /exchangerate/{code_pair}`

*Get Exchange Rate*

<h3 id="currency-exchange-get_exchange_rate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|code_pair|path|string|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0
}
```

<h3 id="currency-exchange-get_exchange_rate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ExchangeRateOutSchema](#schemaexchangerateoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad data in request|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Rate not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: exch_rate:request ), OAuth2PasswordBearer
</aside>

## Currency exchange-update_exchange_rate

<a id="opIdCurrency exchange-update_exchange_rate"></a>

`PATCH /exchangerate/{code_pair}`

*Update Exchange Rate*

> Body parameter

```yaml
rate: 0

```

<h3 id="currency-exchange-update_exchange_rate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|code_pair|path|string|true|none|
|body|body|[UpdateExchangeRateSchema](#schemaupdateexchangerateschema)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0
}
```

<h3 id="currency-exchange-update_exchange_rate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ExchangeRateOutSchema](#schemaexchangerateoutschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad data in request|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency(ies) not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: exch_rate:update ), OAuth2PasswordBearer
</aside>

## Currency exchange-delete_exchange_rate

<a id="opIdCurrency exchange-delete_exchange_rate"></a>

`DELETE /exchangerate/{code_pair}`

*Delete Exchange Rate*

<h3 id="currency-exchange-delete_exchange_rate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|code_pair|path|string|true|none|

> Example responses

> 200 Response

```json
null
```

<h3 id="currency-exchange-delete_exchange_rate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request data|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Currency(ies) not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<h3 id="currency-exchange-delete_exchange_rate-responseschema">Response Schema</h3>

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all ), OAuth2PasswordBearer
</aside>

## Currency exchange-convert_currencies

<a id="opIdCurrency exchange-convert_currencies"></a>

`GET /exchange`

*Convert Currencies*

<h3 id="currency-exchange-convert_currencies-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|from_|query|string|true|none|
|to|query|string|true|none|
|amount|query|number|true|none|

> Example responses

> 200 Response

```json
{
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0,
  "amount": 0,
  "convertedAmount": 0
}
```

<h3 id="currency-exchange-convert_currencies-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[ConvertedCurrencySchema](#schemaconvertedcurrencyschema)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Bad request data|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|Exchange rate not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: exch_rate:request ), OAuth2PasswordBearer
</aside>

<h1 id="fastapi-auth">auth</h1>

## auth-create_user

<a id="opIdauth-create_user"></a>

`POST /clients/register`

*Create User*

> Body parameter

```yaml
username: string
password1: string
password2: string

```

<h3 id="auth-create_user-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_auth-create_user](#schemabody_auth-create_user)|true|none|

> Example responses

> 201 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="auth-create_user-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|Successful Response|[UserCreatedResponse](#schemausercreatedresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Submitted values invalid|[UserCreationErrorResponse](#schemausercreationerrorresponse)|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|User already exists|[UserCreationErrorResponse](#schemausercreationerrorresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## auth-create_token

<a id="opIdauth-create_token"></a>

`POST /tokens/gain`

*Create Token*

> Body parameter

```yaml
device_id: none
grant_type: string
username: string
password: string
scope: ""
client_id: string
client_secret: string

```

<h3 id="auth-create_token-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_auth-create_token](#schemabody_auth-create_token)|true|none|

> Example responses

> 200 Response

```json
{
  "access_token": "string",
  "token_type": "string",
  "access_expires_in": "string",
  "refresh_token": "string",
  "refresh_expires_in": "string",
  "scope": [
    "string"
  ]
}
```

<h3 id="auth-create_token-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[TokenCreatedResponse](#schematokencreatedresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Invalid credentials|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|User disabled|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## auth-refresh_access_token

<a id="opIdauth-refresh_access_token"></a>

`POST /tokens/refresh`

*Refresh Access Token*

> Body parameter

```yaml
grant_type: refresh_token
refresh_token: string

```

<h3 id="auth-refresh_access_token-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_auth-refresh_access_token](#schemabody_auth-refresh_access_token)|true|none|

> Example responses

> 200 Response

```json
{
  "access_token": "string",
  "token_type": "string",
  "access_expires_in": "string",
  "refresh_token": "string",
  "refresh_expires_in": "string",
  "scope": [
    "string"
  ]
}
```

<h3 id="auth-refresh_access_token-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[TokenCreatedResponse](#schematokencreatedresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Token is invalid|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Invalid credentials|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|User disabled or token owner is not a user, or token is revoked|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
HTTPBasic
</aside>

## auth-revoke_users_token

<a id="opIdauth-revoke_users_token"></a>

`PATCH /tokens/revoke`

*Revoke Users Token*

> Body parameter

```yaml
tokens:
  - string

```

<h3 id="auth-revoke_users_token-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[Body_auth-revoke_users_token](#schemabody_auth-revoke_users_token)|false|none|

> Example responses

> 200 Response

```json
{
  "revoked": [
    "string"
  ]
}
```

<h3 id="auth-revoke_users_token-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[TokensRevokedResponse](#schematokensrevokedresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Invalid credentials|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|User disabled|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
HTTPBasic
</aside>

<h1 id="fastapi-users">users</h1>

## users-get_user

<a id="opIdusers-get_user"></a>

`GET /admin/users/search`

*Get User*

<h3 id="users-get_user-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|username|query|string|true|none|

> Example responses

> 200 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="users-get_user-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserOut](#schemauserout)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

## users-get_all_users

<a id="opIdusers-get_all_users"></a>

`GET /admin/users/all`

*Get All Users*

> Example responses

> 200 Response

```json
[
  {
    "username": "string",
    "category": "API_CLIENT",
    "is_active": true,
    "id": 0
  }
]
```

<h3 id="users-get_all_users-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|Inline|

<h3 id="users-get_all_users-responseschema">Response Schema</h3>

Status Code **200**

*Response Users-Get All Users*

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Response Users-Get All Users|[[UserOut](#schemauserout)]|false|none|none|
|» UserOut|[UserOut](#schemauserout)|false|none|none|
|»» username|string|true|none|none|
|»» category|[UserCategory](#schemausercategory)|false|none|none|
|»» is_active|boolean|false|none|none|
|»» id|integer|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|category|API_CLIENT|
|category|ANONYMOUS_CLIENT|
|category|ADMIN|
|category|MANAGER|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

## users-make_user_inactive

<a id="opIdusers-make_user_inactive"></a>

`PATCH /admin/users/{user_id}/deactivate`

*Make User Inactive*

<h3 id="users-make_user_inactive-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|integer|true|none|

> Example responses

> 200 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="users-make_user_inactive-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserOut](#schemauserout)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|User already deactivated or user is admin|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

## users-make_user_active

<a id="opIdusers-make_user_active"></a>

`PATCH /admin/users/{user_id}/activate`

*Make User Active*

<h3 id="users-make_user_active-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|integer|true|none|

> Example responses

> 200 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="users-make_user_active-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserOut](#schemauserout)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|User is already active or user is admin|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

## users-promote_users_category

<a id="opIdusers-promote_users_category"></a>

`PATCH /admin/users/{user_id}/category/promote`

*Promote Users Category*

<h3 id="users-promote_users_category-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|integer|true|none|
|to|query|[TransitionUsersCategories](#schematransitionuserscategories)|true|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|to|1|
|to|0|
|to|-1|

> Example responses

> 200 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="users-promote_users_category-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserOut](#schemauserout)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Performed update conflicts with current state of user category|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

## users-downgrade_users_category

<a id="opIdusers-downgrade_users_category"></a>

`PATCH /admin/users/{user_id}/category/downgrade`

*Downgrade Users Category*

<h3 id="users-downgrade_users_category-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|user_id|path|integer|true|none|
|to|query|[TransitionUsersCategories](#schematransitionuserscategories)|true|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|to|1|
|to|0|
|to|-1|

> Example responses

> 200 Response

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}
```

<h3 id="users-downgrade_users_category-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[UserOut](#schemauserout)|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|User not found|None|
|409|[Conflict](https://tools.ietf.org/html/rfc7231#section-6.5.8)|Performed update conflicts with current state of user category|None|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
OAuth2PasswordBearer ( Scopes: all )
</aside>

# Schemas

<h2 id="tocS_AddCurrencySchema">AddCurrencySchema</h2>
<!-- backwards compatibility -->
<a id="schemaaddcurrencyschema"></a>
<a id="schema_AddCurrencySchema"></a>
<a id="tocSaddcurrencyschema"></a>
<a id="tocsaddcurrencyschema"></a>

```json
{
  "name": "string",
  "code": "string",
  "sign": "string"
}

```

AddCurrencySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|code|string|true|none|none|
|sign|string|true|none|none|

<h2 id="tocS_AddExchangeRateSchema">AddExchangeRateSchema</h2>
<!-- backwards compatibility -->
<a id="schemaaddexchangerateschema"></a>
<a id="schema_AddExchangeRateSchema"></a>
<a id="tocSaddexchangerateschema"></a>
<a id="tocsaddexchangerateschema"></a>

```json
{
  "baseCurrencyCode": "string",
  "targetCurrencyCode": "string",
  "rate": 0
}

```

AddExchangeRateSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|baseCurrencyCode|string|true|none|none|
|targetCurrencyCode|string|true|none|none|
|rate|number|true|none|none|

<h2 id="tocS_Body_auth-create_token">Body_auth-create_token</h2>
<!-- backwards compatibility -->
<a id="schemabody_auth-create_token"></a>
<a id="schema_Body_auth-create_token"></a>
<a id="tocSbody_auth-create_token"></a>
<a id="tocsbody_auth-create_token"></a>

```json
{
  "device_id": "none",
  "grant_type": "string",
  "username": "string",
  "password": "string",
  "scope": "",
  "client_id": "string",
  "client_secret": "string"
}

```

Body_auth-create_token

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|device_id|string|false|none|none|
|grant_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|username|string|true|none|none|
|password|string|true|none|none|
|scope|string|false|none|none|
|client_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|client_secret|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_Body_auth-create_user">Body_auth-create_user</h2>
<!-- backwards compatibility -->
<a id="schemabody_auth-create_user"></a>
<a id="schema_Body_auth-create_user"></a>
<a id="tocSbody_auth-create_user"></a>
<a id="tocsbody_auth-create_user"></a>

```json
{
  "username": "string",
  "password1": "string",
  "password2": "string"
}

```

Body_auth-create_user

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|username|string|true|none|none|
|password1|string|true|none|none|
|password2|string|true|none|none|

<h2 id="tocS_Body_auth-refresh_access_token">Body_auth-refresh_access_token</h2>
<!-- backwards compatibility -->
<a id="schemabody_auth-refresh_access_token"></a>
<a id="schema_Body_auth-refresh_access_token"></a>
<a id="tocSbody_auth-refresh_access_token"></a>
<a id="tocsbody_auth-refresh_access_token"></a>

```json
{
  "grant_type": "refresh_token",
  "refresh_token": "string"
}

```

Body_auth-refresh_access_token

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|grant_type|string|true|none|Required to be an exact "refresh_token" value|
|refresh_token|string|true|none|none|

<h2 id="tocS_Body_auth-revoke_users_token">Body_auth-revoke_users_token</h2>
<!-- backwards compatibility -->
<a id="schemabody_auth-revoke_users_token"></a>
<a id="schema_Body_auth-revoke_users_token"></a>
<a id="tocSbody_auth-revoke_users_token"></a>
<a id="tocsbody_auth-revoke_users_token"></a>

```json
{
  "tokens": [
    "string"
  ]
}

```

Body_auth-revoke_users_token

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tokens|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[string]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ConvertedCurrencySchema">ConvertedCurrencySchema</h2>
<!-- backwards compatibility -->
<a id="schemaconvertedcurrencyschema"></a>
<a id="schema_ConvertedCurrencySchema"></a>
<a id="tocSconvertedcurrencyschema"></a>
<a id="tocsconvertedcurrencyschema"></a>

```json
{
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0,
  "amount": 0,
  "convertedAmount": 0
}

```

ConvertedCurrencySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|baseCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|targetCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|rate|number|true|none|none|
|amount|number|true|none|none|
|convertedAmount|number|true|none|none|

<h2 id="tocS_CurrencyOutSchema">CurrencyOutSchema</h2>
<!-- backwards compatibility -->
<a id="schemacurrencyoutschema"></a>
<a id="schema_CurrencyOutSchema"></a>
<a id="tocScurrencyoutschema"></a>
<a id="tocscurrencyoutschema"></a>

```json
{
  "id": 0,
  "name": "string",
  "code": "string",
  "sign": "string"
}

```

CurrencyOutSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|true|none|none|
|name|string|true|none|none|
|code|string|true|none|none|
|sign|string|true|none|none|

<h2 id="tocS_ExchangeRateOutSchema">ExchangeRateOutSchema</h2>
<!-- backwards compatibility -->
<a id="schemaexchangerateoutschema"></a>
<a id="schema_ExchangeRateOutSchema"></a>
<a id="tocSexchangerateoutschema"></a>
<a id="tocsexchangerateoutschema"></a>

```json
{
  "id": 0,
  "baseCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "targetCurrency": {
    "id": 0,
    "name": "string",
    "code": "string",
    "sign": "string"
  },
  "rate": 0
}

```

ExchangeRateOutSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|true|none|none|
|baseCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|targetCurrency|[CurrencyOutSchema](#schemacurrencyoutschema)|true|none|none|
|rate|number|true|none|none|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_TokenCreatedResponse">TokenCreatedResponse</h2>
<!-- backwards compatibility -->
<a id="schematokencreatedresponse"></a>
<a id="schema_TokenCreatedResponse"></a>
<a id="tocStokencreatedresponse"></a>
<a id="tocstokencreatedresponse"></a>

```json
{
  "access_token": "string",
  "token_type": "string",
  "access_expires_in": "string",
  "refresh_token": "string",
  "refresh_expires_in": "string",
  "scope": [
    "string"
  ]
}

```

TokenCreatedResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|access_token|string|true|none|none|
|token_type|string|true|none|none|
|access_expires_in|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(duration)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|refresh_token|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|refresh_expires_in|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(duration)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|scope|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[string]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_TokensRevokedResponse">TokensRevokedResponse</h2>
<!-- backwards compatibility -->
<a id="schematokensrevokedresponse"></a>
<a id="schema_TokensRevokedResponse"></a>
<a id="tocStokensrevokedresponse"></a>
<a id="tocstokensrevokedresponse"></a>

```json
{
  "revoked": [
    "string"
  ]
}

```

TokensRevokedResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|revoked|[string]|true|none|none|

<h2 id="tocS_TransitionUsersCategories">TransitionUsersCategories</h2>
<!-- backwards compatibility -->
<a id="schematransitionuserscategories"></a>
<a id="schema_TransitionUsersCategories"></a>
<a id="tocStransitionuserscategories"></a>
<a id="tocstransitionuserscategories"></a>

```json
1

```

TransitionUsersCategories

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TransitionUsersCategories|integer|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TransitionUsersCategories|1|
|TransitionUsersCategories|0|
|TransitionUsersCategories|-1|

<h2 id="tocS_UpdateCurrencySchema">UpdateCurrencySchema</h2>
<!-- backwards compatibility -->
<a id="schemaupdatecurrencyschema"></a>
<a id="schema_UpdateCurrencySchema"></a>
<a id="tocSupdatecurrencyschema"></a>
<a id="tocsupdatecurrencyschema"></a>

```json
{
  "name": "string",
  "sign": "string"
}

```

UpdateCurrencySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|name|string|true|none|none|
|sign|string|true|none|none|

<h2 id="tocS_UpdateExchangeRateSchema">UpdateExchangeRateSchema</h2>
<!-- backwards compatibility -->
<a id="schemaupdateexchangerateschema"></a>
<a id="schema_UpdateExchangeRateSchema"></a>
<a id="tocSupdateexchangerateschema"></a>
<a id="tocsupdateexchangerateschema"></a>

```json
{
  "rate": 0
}

```

UpdateExchangeRateSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|rate|number|true|none|none|

<h2 id="tocS_UserCategory">UserCategory</h2>
<!-- backwards compatibility -->
<a id="schemausercategory"></a>
<a id="schema_UserCategory"></a>
<a id="tocSusercategory"></a>
<a id="tocsusercategory"></a>

```json
"API_CLIENT"

```

UserCategory

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|UserCategory|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|UserCategory|API_CLIENT|
|UserCategory|ANONYMOUS_CLIENT|
|UserCategory|ADMIN|
|UserCategory|MANAGER|

<h2 id="tocS_UserCreatedResponse">UserCreatedResponse</h2>
<!-- backwards compatibility -->
<a id="schemausercreatedresponse"></a>
<a id="schema_UserCreatedResponse"></a>
<a id="tocSusercreatedresponse"></a>
<a id="tocsusercreatedresponse"></a>

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}

```

UserCreatedResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|username|string|true|none|none|
|category|[UserCategory](#schemausercategory)|false|none|none|
|is_active|boolean|false|none|none|
|id|integer|true|none|none|

<h2 id="tocS_UserCreationErrorResponse">UserCreationErrorResponse</h2>
<!-- backwards compatibility -->
<a id="schemausercreationerrorresponse"></a>
<a id="schema_UserCreationErrorResponse"></a>
<a id="tocSusercreationerrorresponse"></a>
<a id="tocsusercreationerrorresponse"></a>

```json
{
  "errors": {
    "password": [
      "Minimum password length must be 8",
      "Password should consist of ..."
    ],
    "username": [
      "Minimum username length must be 5",
      "Username should consist of ..."
    ]
  }
}

```

UserCreationErrorResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|errors|object|true|none|none|
|» **additionalProperties**|[string]|false|none|none|

<h2 id="tocS_UserOut">UserOut</h2>
<!-- backwards compatibility -->
<a id="schemauserout"></a>
<a id="schema_UserOut"></a>
<a id="tocSuserout"></a>
<a id="tocsuserout"></a>

```json
{
  "username": "string",
  "category": "API_CLIENT",
  "is_active": true,
  "id": 0
}

```

UserOut

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|username|string|true|none|none|
|category|[UserCategory](#schemausercategory)|false|none|none|
|is_active|boolean|false|none|none|
|id|integer|true|none|none|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|

