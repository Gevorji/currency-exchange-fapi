from abc import ABC, abstractmethod


class RepositoryABC(ABC):

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        ...

    @abstractmethod
    async def get(self, *args, **kwargs):
        ...

    @abstractmethod
    async def save(self, *args, **kwargs):
        ...

    @abstractmethod
    async def update(self, *args, **kwargs):
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs):
        ...


class BulkOperationsRepository(ABC):

    @abstractmethod
    async def bulk_save(self, *args, **kwargs):
        ...

    @abstractmethod
    async def bulk_delete(self, *args, **kwargs):
        ...

    @abstractmethod
    async def bulk_update(self, *args, **kwargs):
        ...
