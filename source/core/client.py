from typing import Callable, Coroutine

from aiogram import Dispatcher, Bot
from aiogram.filters import Command


class AiogramClient:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.bot: Bot = None  # type: ignore

    def command(self, name: str = None):
        def wrapper(func: Callable[..., Coroutine]):
            command_name: str = name or func.__name__

            self.dispatcher.message(Command(commands=[command_name]))(func)

        return wrapper

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        self.dispatcher.run_polling(self.bot)


AiogramBot = AiogramClient