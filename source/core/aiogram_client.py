from typing import Callable, Coroutine, Any
from functools import wraps
import inspect

from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import BotCommand, Message


class AiogramClient:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.bot: Bot = None  # type: ignore

    @staticmethod
    def _parse_message_args(message: Message, annotations: dict[str, type]) -> dict[str, Any]:
        raw = message.text.split(maxsplit=1)[1]  # Remove command text
        kwargs = {}
        print("annotations", annotations)

        for arg, value in zip(annotations, raw.split()):
            print(arg)
            print("value", value)
            kwargs[arg] = annotations[arg](value)


        return kwargs    

    def command(self, name: str = None, description: str = "No description."):
        def wrapper(func: Callable[..., Coroutine]):
            command_name: str = name or func.__name__
            func_args = func.__code__.co_varnames[1:func.__code__.co_argcount]

            annotated = {}
            for arg in func_args:
                if arg in func.__annotations__:
                    annotated[arg] = func.__annotations__[arg]
                else:
                    annotated[arg] = str

            @wraps(func)
            async def wrapped(message: Message):
                kwargs = self._parse_message_args(message, annotated)

                return await func(message, **kwargs)

            self.dispatcher.message(Command(BotCommand(command=command_name, description=description)))(wrapped)

        return wrapper

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        self.dispatcher.run_polling(self.bot)

    async def astart(self, token: str):
        self.bot = Bot(token, parse_mode="HTML")
        await self.dispatcher.start_polling(self.bot)
