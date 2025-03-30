from typing import Callable, TypeVar

import sqlalchemy
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from pydantic import BaseModel as PydanticModel

SessionMakerType: async_sessionmaker[AsyncSession]

InputModelType = TypeVar("InputModelType", bound=PydanticModel)
OutputModelType = TypeVar("OutputModelType", bound=PydanticModel)
RootModelType = TypeVar("RootModelType", bound=DeclarativeBase)
ExceptionType = TypeVar("ExceptionType", bound=type[Exception])


class AsyncCrudMixin[RootModelType, InputModelType, OutputModelType]:
    _root_model: RootModelType
    _object_does_not_exist_error: ExceptionType
    _input_model: InputModelType
    _output_model: OutputModelType
    _session_factory: SessionMakerType
    create_root_model_from_dto: Callable[[InputModelType], RootModelType]

    async def _get_object(self, identity_criteria, error_msg: str) -> OutputModelType:
        async with self._session_factory() as session:
            async with session.begin():
                res = await session.execute(select(self._root_model).where(identity_criteria))
                model = res.scalars().one_or_none()
                if model is None:
                    raise self._object_does_not_exist_error(error_msg)

        return self._output_model.model_validate(model)

    async def _get_all_objects(self) -> list[OutputModelType]:
        async with self._session_factory() as session:
            async with session.begin():
                res = await session.execute(select(self._root_model))
        return [self._output_model.model_validate(obj) for obj in res.scalars().all()]

    async def _save_object(self, input_object) -> None:
        model = self.create_root_model_from_dto(input_object)
        async with self._session_factory() as session:
            async with session.begin():
                self.process_final_model(model)
                session.add(model)

    async def _update_object(self, identity_criteria, update_values: dict, error_msg: str) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                res = await session.execute(select(self._root_model).where(identity_criteria))
                model = res.scalars().one_or_none()
                if not model:
                    raise self._object_does_not_exist_error(error_msg)

                for attr, value in update_values.items():
                    setattr(model, attr, value)
                self.process_final_model(model)

    async def _delete_object(self, identity_criteria, error_msg: str) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                res = await session.execute(select(self._root_model).where(identity_criteria))
                model = res.scalars().one_or_none()
                if model is None:
                    raise self._object_does_not_exist_error(error_msg)
                session.delete(model)

    def process_final_model(self, model: RootModelType) -> None: ...



