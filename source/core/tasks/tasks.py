import asyncio
from typing import Callable, Coroutine

__all__ = ("create_task", "Task")


def create_task(interval: int):
    def wrapper(coro: Callable[..., Coroutine]):
        return Task(coro, interval)

    return wrapper


class Task:
    def __init__(self, coro: Callable[..., Coroutine], interval: int):
        self.coro: Callable[..., Coroutine] = coro
        self.interval: int = interval

        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = asyncio.Event()

    def start(self):
        self._loop = asyncio.get_event_loop()
        self._running.set()
        self._loop.create_task(self.run())

    async def run(self):
        while self._running.is_set():
            self._loop.create_task(self.coro())
            await asyncio.sleep(self.interval)

    def stop(self):
        self._running.clear()
