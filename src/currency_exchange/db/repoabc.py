from abc import ABC, abstractmethod


class RepositoryABC(ABC):

    @abstractmethod
    async def get_all(self):
        ...

    @abstractmethod
    async def get(self):
        ...

    @abstractmethod
    async def save(self):
        ...

    @abstractmethod
    async def update(self):
        ...

    @abstractmethod
    async def delete(self):
        ...


class BulkOperationsRepository(ABC):

    @abstractmethod
    async def bulk_save(self):
        ...

    @abstractmethod
    async def bulk_delete(self):
        ...

    @abstractmethod
    async def bulk_update(self):
        ...
