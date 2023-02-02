from typing import TYPE_CHECKING

from .abc import CursedTypedDict
from .variables import VarChar

if TYPE_CHECKING:
    from .client import PostgreClient


class BaseTable(CursedTypedDict):
    __table_name__: str | None = None
    client: "PostgreClient"

    def __new__(cls, *args, **kwargs):
        cls._variables = cls._sql_vars_from_annotations()
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        if table_name := kwargs.get("name"):
            cls.__table_name__ = table_name

    @property
    def table_name(self) -> str:
        return (self.__table_name__ or self.__class__.__name__).lower()

    @classmethod
    def _sql_vars_from_annotations(cls) -> list[str]:
        variables: list[str] = []
        annotations = cls.__all_annotations__()

        for attr_name, type in annotations.items():
            if (attr_name.startswith("__") and attr_name.endswith("__")) or attr_name == "client":
                continue

            is_null = attr_name in cls.__dict__

            if attr_name == "id" and type is int:
                variables.append("id SERIAL PRIMARY KEY")
                continue

            variables.append(
                f"{attr_name} {cls._convert_type(type)}{' NOT NULL' if not is_null else ''}"
            )

        return variables

    @staticmethod
    def _convert_type(type_) -> str:
        if isinstance(type_, VarChar):
            return f"VARCHAR({type_.max_chars})"

        return {
            int: "INTEGER",
            str: "TEXT",
        }.get(type_, str(type_))

    @classmethod
    def _create_request_string(cls, check_for_exists: bool = True) -> str:
        variables = ",".join(cls._variables)

        return f"CREATE TABLE {'IF NOT EXISTS' if check_for_exists else ''} " \
               f"{cls.table_name} (" \
               f"{variables}" \
               ")"

    def _insert_request_string(self) -> str:
        json = self.json
        keys = ", ".join(json.keys())
        values = ", ".join(json.values())
        return f"INSERT INTO {self.table_name} ({keys}) VALUES ({values})"

    @classmethod
    async def create(self):
        await self.client.connection.execute(self._create_request_string())

    async def insert(self):
        await self.client.connection.execute(self._insert_request_string())


class TestTable(BaseTable, name="testtable"):
    id: int
    name: VarChar(100)
