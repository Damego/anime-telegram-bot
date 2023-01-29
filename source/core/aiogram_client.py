from typing import Callable, Coroutine

from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import BotCommand


class AiogramClient:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.bot: Bot = None  # type: ignore

    def command(self, name: str = None, description: str = "No description."):
        def wrapper(func: Callable[..., Coroutine]):
            command_name: str = name or func.__name__

            self.dispatcher.message(Command(BotCommand(command=command_name, description=description)))(func)

        return wrapper

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        self.dispatcher.run_polling(self.bot)

    async def astart(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        await self.dispatcher.start_polling(self.bot)
