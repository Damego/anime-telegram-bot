class VarChar:
    def __init__(self, max_chars: int):
        self.max_chars: int = max_chars


class BaseModel:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__types = cls.__parse_annotations()
        return instance

    @classmethod
    def __parse_annotations(cls) -> list[str]:
        annotations: list[str] = []

        for attr_name, type in cls.__annotations__.items():
            is_null = attr_name in cls.__dict__

            if attr_name == "id":
                annotations.append("id SERIAL PRIMARY KEY")
                continue

            annotations.append(
                f"{attr_name} {cls._convert_type(type)} {'NOT NULL' if not is_null else ''}"
            )

        return annotations

    @staticmethod
    def _convert_type(type_: type) -> str:
        if isinstance(type_, VarChar):
            return f"VARCHAR({type_.max_chars})"

        return {
            int: "INTEGER",
            str: "TEXT",
        }.get(type_)

    def create(self, name: str = None, check_for_exists: bool = True) -> str:
        types = ",\n".join(self.__types)

        return f"CREATE TABLE {'IF NOT EXISTS' if check_for_exists else ''} {name or self.__class__.__name__.lower()} (" \
               f"\n{types}" \
               "\n)"


class MyTable(BaseModel):
    id: int
    name: VarChar(50)
    f: str = None


table = MyTable(
    name="asf"
)
print(table.create())