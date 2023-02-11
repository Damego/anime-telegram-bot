from inspect import getdoc, signature
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from aiogram.dispatcher.router import Router
from aiogram.types import Message

if TYPE_CHECKING:
    from .client import AiogramClient
    from .extensions import ExtensionRouter


__all__ = ("Command",)


class Command:
    client: "AiogramClient"
    extension: Optional["ExtensionRouter"]
    router: Router

    def __init__(
        self,
        coro: Callable[..., Coroutine],
        name: str | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
    ):
        self._coro = coro
        self.name = name or coro.__name__
        self.description = description or getdoc(coro) or "No description."
        self.aliases = aliases

        self.extension = None

    async def call(self, message: Message):
        kwargs = self.get_command_args(message)

        if self.extension is not None:
            response = await self._coro(self.extension, message, **kwargs)
        else:
            response = await self._coro(message, **kwargs)

        # Allow to do `return "text"`
        if isinstance(response, str):
            await message.answer(response)

    def get_command_args(self, message: Message) -> dict[str, Any]:
        raw_args = message.text.split(maxsplit=1)

        split_limit = 1 if self.extension is None else 2

        if len(raw_args) == 1:
            return {}

        raw_args = raw_args[1]  # Remove command text
        parameters = list(signature(self._coro).parameters.values())[
            split_limit:
        ]  # Ignore message parameter

        if not parameters:
            return {}

        if len(parameters) == 1:
            param = parameters[0]
            if param.annotation in {str, param.empty}:
                return {param.name: raw_args}

        kwargs = {}
        last_param = parameters[-1]

        for param in parameters:
            if last_param.name != param.name:
                value, raw_args = raw_args.split(maxsplit=1)
            else:
                value = raw_args

            kwargs[param.name] = (
                param.annotation(value) if param.annotation not in {str, param.empty} else value
            )

        return kwargs
