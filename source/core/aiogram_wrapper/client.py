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

    def command(self, name: Optional[str] = None, description: Optional[str] = None):
        def wrapper(func: Callable[..., Coroutine]):
            command_name: str = name or func.__name__
            command_description: str = description or "No description."

            func_args = func.__code__.co_varnames[1:func.__code__.co_argcount]
            annotated = {
                arg: func.__annotations__[arg] if arg in func.__annotations__ else str
                for arg in func_args
            }

            async def wrapped(message: Message):
                kwargs = get_command_args(message, annotated)

                response = await func(message, **kwargs)
                if isinstance(response, str):
                    await message.answer(response)

            self.dispatcher.message(
                Command(BotCommand(command=command_name, description=command_description))
            )(wrapped)

        return wrapper

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        self.dispatcher.run_polling(self.bot)

    async def astart(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        await self.dispatcher.start_polling(self.bot)
