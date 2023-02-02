from typing import Any

__all__ = ("CursedTypedDict", )


# Not a typed dict because there are no dict helper methods
# Not a typed tuple because you can't iterate over it
# What is it then?
class CursedTypedDict:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        if data := kwargs or cls.__kwargs_from_args(args):
            for key, value in data.items():
                setattr(instance, key, value)

        return instance

    @classmethod
    def __kwargs_from_args(cls, args) -> dict[str, Any]:
        return {
            key: arg
            for key, arg in zip(cls.__all_annotations__(), args)
        }

    @classmethod
    def __all_annotations__(cls) -> dict[str, type]:
        annotation_list = []
        _class = cls

        while _class is not CursedTypedDict:
            annotation_list.extend(
                [
                    (k, v)
                    for k, v in _class.__annotations__.items()
                    if not (k.startswith("__") and k.endswith("__"))
                ][::-1]
            )
            _class = _class.__base__

        return {k: v for k, v in annotation_list[::-1]}

    @property
    def json(self) -> dict:
        json = {
            k: getattr(self, k)
            for k in self.__all_annotations__()
        }

        return json
