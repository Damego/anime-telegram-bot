import inspect
from asyncio import iscoroutinefunction
from functools import wraps
from typing import Callable, Coroutine

from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.dispatcher.router import Router

from .client import AiogramClient
from .command import Command

__all__ = ("ExtensionRouter", "command", "message", "callback_query")


class ExtensionRouter:
    client: AiogramClient
    router: Router

    def __new__(cls, client: AiogramClient, *args, **kwargs):
        self = super().__new__(cls)
        self.client = client
        self.router = Router(name=cls.__name__)

        self.__register_handlers()

        return self

    def __register_handlers(self):
        for func_name, func in inspect.getmembers(self, predicate=iscoroutinefunction):
            if func_name.startswith("__") and func_name.endswith("__"):
                continue  # Skip dunder methods
            if not hasattr(func, "__handler_data__"):
                continue  # Skip not handler methods

            name, args, kwargs = func.__handler_data__

            observer: TelegramEventObserver = getattr(self.router, name)
            observer.register(func, *args, **kwargs)

        for func_name, cmd in inspect.getmembers(
            self, predicate=lambda _func: isinstance(_func, Command)
        ):
            cmd: Command

            cmd.client = self.client
            cmd.extension = self
            cmd.router = self.router

            self.client._commands.append(cmd)

        self.client.dispatcher.include_router(self.router)


@wraps(TelegramEventObserver.__call__)
def _handler(handler_name: str, *args, **kwargs):
    def wrapper(coro: Callable[..., Coroutine]):
        coro.__handler_data__ = handler_name, args, kwargs

        return coro

    return wrapper


@wraps(TelegramEventObserver.__call__)
def message(*args, **kwargs):
    return _handler("message", *args, **kwargs)


@wraps(TelegramEventObserver.__call__)
def callback_query(*args, **kwargs):
    return _handler("callback_query", *args, **kwargs)


@wraps(AiogramClient.command)
def command(*args, **kwargs):
    def decorator(coro: Callable[..., Coroutine]):
        _command = Command(coro, *args, **kwargs)
        return _command

    return decorator
