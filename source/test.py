class VarChar:
    def __init__(self, max_chars: int):
        self.max_chars: int = max_chars


class BaseModel:
    def __new__(cls, *args, **kwargs):
        print(cls.__annotations__)
        print(cls.__dict__)

        return super().__new__(cls)

    def parse_annotations(self) -> list[str]:
        annotations: list[str] = []

        for attr_name, type in self.__annotations__.items():
            is_null = attr_name in self.__dict__

            if attr_name == "id":
                annotations.append("id SERIAL PRIMARY KEY")
                continue

            annotations.append(
                f"{attr_name} {self._convert_type(type)} {'NOT NULL' if not is_null else ''}"
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


class Table(BaseModel):
    id: int
    name: VarChar(50)
    f: str = None


table = Table(
    name="asf"
)
print(table.parse_annotations())