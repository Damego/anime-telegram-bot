from typing import Callable, Coroutine, Optional

from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

from .message_parsers import get_command_args

__all__ = ("AiogramClient", )


class AiogramClient:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.bot: Bot = None  # type: ignore

    def command(self, name: Optional[str] = None, description: Optional[str] = None, aliases: list[str] | None = None):
        def wrapper(coro: Callable[..., Coroutine]):
            command_name: str = name or coro.__name__
            command_description: str = description or "No description."

            async def wrapped(message: Message):
                kwargs = get_command_args(coro, message)

                response = await coro(message, **kwargs)
                if isinstance(response, str):
                    await message.answer(response)

            self.dispatcher.message(
                Command(BotCommand(command=command_name, description=command_description), commands=aliases)
            )(wrapped)

        return wrapper

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="MarkdownV2")
        self.dispatcher.run_polling(self.bot)

    async def astart(self, token: str):
        self.bot = Bot(token, parse_mode="MarkdownV2")
        await self.dispatcher.start_polling(self.bot)
