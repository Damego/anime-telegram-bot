from typing import Callable, Coroutine, TYPE_CHECKING, Optional
from inspect import getdoc

from aiogram.dispatcher.router import Router
from aiogram.types import Message

from .message_parsers import get_command_args

if TYPE_CHECKING:
    from .client import AiogramClient
    from .extensions import ExtensionRouter


class Command:
    client: "AiogramClient"
    extension: Optional["ExtensionRouter"]
    router: Router

    def __init__(self, coro: Callable[..., Coroutine], name: str | None = None, description: str | None = None, aliases: list[str] | None = None):
        self._coro = coro
        self.name = name or coro.__name__
        self.description = description or getdoc(coro) or "No description."
        self.aliases = aliases

        self.extension = None

    async def call(self, message: Message):
        kwargs = get_command_args(self._coro, message)

        if self.extension is not None:
            response = await self._coro(self.extension, message, **kwargs)
        else:
            response = await self._coro(message, **kwargs)

        # Allow to do `return "text"`
        if isinstance(response, str):
            await message.answer(response)

