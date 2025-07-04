class CurrencyCoreError(Exception): ...


class IncorrectCurrencyCodeError(CurrencyCoreError): ...


class CrossExchangeRateComputationError(CurrencyCoreError): ...


class IncorrectExchangeRateValue(CurrencyCoreError): ...


class IncorrectCurrencyAmount(CurrencyCoreError): ...


class IncorrectCurrencyName(CurrencyCoreError): ...


class IncorrectCurrencySign(CurrencyCoreError): ...
