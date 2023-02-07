from typing import Any

from aiogram.types import Message

__all__ = ("get_command_args", )


def get_command_args(message: Message, annotations: dict[str, type]) -> dict[str, Any]:
    raw = message.text.split(maxsplit=1)[1]  # Remove command text
    return {
        arg: annotations[arg](value)
        for arg, value in zip(annotations, raw.split())
    }