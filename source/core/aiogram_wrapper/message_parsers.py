from typing import Any, Callable, Coroutine
from inspect import signature

from aiogram.types import Message

__all__ = ("get_command_args", )


def get_command_args(coro: Callable[..., Coroutine], message: Message) -> dict[str, Any]:
    raw_args = message.text.split(maxsplit=1)[1]  # Remove command text
    parameters = list(signature(coro).parameters.values())[1:]  # Ignore message parameter

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

        kwargs[param.name] = param.annotation(value) if param.annotation not in {str, param.empty} else value

    return kwargs

