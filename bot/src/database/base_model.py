from typing import List, TypeVar, Generic, Type
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from database.database_config import DatabaseConfig


T = TypeVar('T', bound='BaseModel')


class Base(DeclarativeBase):
    pass


class BaseModel(Base, Generic[T]):
    """Base model for all database models that contains common methods"""
    __database__: DatabaseConfig = None
    __abstract__ = True
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    async def get(cls: Type[T], pk: object) -> Optional[T]:
        """get instance by pk"""
        async with cls.__database__.async_session_maker() as session:
            try:
                instance: T | None = await session.scalar(select(cls).where(cls.id == pk))
                return instance

            except OperationalError as e:
                print(e)


    @classmethod
    async def filter(cls: Type[T], *args, **kwargs) -> List[T]:
        """get list of instances that match the filter conditions"""
        async with cls.__database__.async_session_maker() as session:
            try:
                result = await session.scalars(select(cls).filter_by(**kwargs))
                return result.all()

            except OperationalError as e:
                print(e)

    @classmethod
    async def all(cls: Type[T]) -> List[T]:
        """get all instances of model"""
        async with cls.__database__.async_session_maker() as session:
            try:
                result = await session.scalars(select(cls))
                return result.all()

            except OperationalError as e:
                print(e)

    async def delete(self) -> None:
        """del current instance from db"""
        async with self.__database__.async_session_maker() as session:
            try:
                await session.delete(self)
                await session.commit()

            except OperationalError as e:
                print(e)

    @classmethod
    async def create(cls: Type[T], **kwargs) -> T:
        """creates new instance of model"""
        async with cls.__database__.async_session_maker() as session:
            try:
                instance: T = cls(**kwargs)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance

            except OperationalError as e:
                print(e)

    async def save(self) -> T:
        """save current instance to the db"""
        async with self.__database__.async_session_maker() as session:
            try:
                await session.execute(
                    update(
                        self.__class__
                    ).where(
                        self.__class__.id == self.id
                    ).values(**{c.name: getattr(self, c.name) for c in self.__table__.columns})
                )
                await session.commit()
                return self

            except OperationalError as e:
                print(e)