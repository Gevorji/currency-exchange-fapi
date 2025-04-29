from ..dto import CurrencyDto, GetCurrencyDto, AddCurrencyDto, AlterCurrencyDto, DeleteCurrencyDto
from ..interfaces import CurrencyRepoInterface


class GetAllCurrenciesInteraction:

     def __init__(self, currencies_repo: CurrencyRepoInterface):
         self._currencies_repo = currencies_repo

     async def __call__(self) -> list[CurrencyDto]:
         return [CurrencyDto.from_dm(currency) for currency in await self._currencies_repo.get_all_currencies()]


class GetCurrencyInteraction:

    def __init__(self, currencies_repo: CurrencyRepoInterface):
        self._currencies_repo = currencies_repo

    async def __call__(self, currency_data: GetCurrencyDto) -> CurrencyDto:
        return CurrencyDto.from_dm(await self._currencies_repo.get_currency(currency_data))


class AddCurrencyInteraction:

    def __init__(self, currencies_repo: CurrencyRepoInterface):
        self._currencies_repo = currencies_repo

    async def __call__(self, currency: AddCurrencyDto) -> CurrencyDto:
        return CurrencyDto.from_dm(await self._currencies_repo.save_currency(currency))


class UpdateCurrencyInteraction:

    def __init__(self, currencies_repo: CurrencyRepoInterface):
        self._currencies_repo = currencies_repo

    async def __call__(self, update_data: AlterCurrencyDto, *args, **kwargs) -> CurrencyDto:
        return CurrencyDto.from_dm(await self._currencies_repo.update_currency(update_data))


class DeleteCurrencyInteraction:

    def __init__(self, currencies_repo: CurrencyRepoInterface):
        self._currencies_repo = currencies_repo

    async def __call__(self, delete_data: DeleteCurrencyDto, *args, **kwargs) -> CurrencyDto:
        return CurrencyDto.from_dm(await self._currencies_repo.delete_currency(delete_data))







