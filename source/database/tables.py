from .abc import CursedTypedDict
from .variables import VarChar


class BaseTable(CursedTypedDict):
    __table_name__: str | None = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance._variables = cls._sql_vars_from_annotations()

        return instance

    def __init_subclass__(cls, **kwargs):
        if table_name := kwargs.get("name"):
            cls.__table_name__ = table_name

    @classmethod
    def _sql_vars_from_annotations(cls) -> list[str]:
        variables: list[str] = []
        annotations = cls.__all_annotations__()

        for attr_name, type in annotations.items():
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            is_null = attr_name in cls.__dict__

            if attr_name == "id":
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

    def get_sql(self, check_for_exists: bool = True) -> str:
        variables = ",".join(self._variables)
        table_name = (self.__table_name__ or self.__class__.__name__).lower()

        return f"CREATE TABLE {'IF NOT EXISTS' if check_for_exists else ''} " \
               f"{table_name} (" \
               f"{variables}" \
               ")"
