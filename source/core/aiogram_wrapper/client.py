from typing import Callable, Coroutine, Optional

from aiogram import Dispatcher, Bot
from aiogram.filters import Command as FilterCommand
from aiogram.types import BotCommand

from .command import Command

__all__ = ("AiogramClient", )


class AiogramClient:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.bot: Bot = None  # type: ignore

        self._commands: list[Command] = []

    def command(self, name: Optional[str] = None, description: Optional[str] = None, aliases: list[str] | None = None):
        def decorator(coro: Callable[..., Coroutine]):
            command_name: str = name or coro.__name__
            command_description: str = description or "No description."

            command = Command(coro, command_name, command_description, aliases)
            command.client = self
            command.router = self.dispatcher

            self._commands.append(command)

            return command

        return decorator

    def __resolve_commands(self):
        for command in self._commands:
            print(command.name)
            command.router.message(
                FilterCommand(BotCommand(command=command.name, description=command.description), commands=command.aliases)
            )(command.call)

    def start(self, token: str):
        self.bot = Bot(token, parse_mode="MarkdownV2")
        self.__resolve_commands()
        self.dispatcher.run_polling(self.bot)

    async def astart(self, token: str):
        self.bot = Bot(token, parse_mode="MarkdownV2")
        self.__resolve_commands()
        await self.dispatcher.start_polling(self.bot)
